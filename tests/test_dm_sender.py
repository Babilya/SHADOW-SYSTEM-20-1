"""
Unit tests for DMSenderService
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dm_sender import DMSenderService, DMTask, DMStatus


class TestDMSenderService:
    """Tests for DMSenderService"""
    
    @pytest.fixture
    def dm_service(self):
        """Create fresh DMSenderService instance"""
        return DMSenderService()
    
    def test_service_initialization(self, dm_service):
        """Test service initializes correctly"""
        assert dm_service.tasks == {}
        assert dm_service.running_tasks == {}
        assert dm_service.blacklist == set()
        assert dm_service.recent_sent == {}
        assert dm_service.stats["total_sent"] == 0
        assert dm_service.stats["total_failed"] == 0
    
    def test_create_task(self, dm_service):
        """Test creating a DM task"""
        task = dm_service.create_task(
            task_id="test-123",
            name="Test Campaign",
            message_template="Hello {name}!",
            target_users=[123, 456, 789],
            interval_min=30,
            interval_max=60
        )
        
        assert task.name == "Test Campaign"
        assert task.target_users == [123, 456, 789]
        assert task.message_template == "Hello {name}!"
        assert task.interval_min == 30
        assert task.interval_max == 60
        assert task.status == DMStatus.PENDING
        assert task.task_id in dm_service.tasks
    
    def test_create_task_with_blacklist(self, dm_service):
        """Test that blacklisted users are excluded"""
        dm_service.blacklist.add(456)
        
        task = dm_service.create_task(
            task_id="test-bl",
            name="Test",
            message_template="Hello!",
            target_users=[123, 456, 789]
        )
        
        assert 456 not in task.target_users
        assert task.target_users == [123, 789]
    
    def test_create_task_with_cooldown(self, dm_service):
        """Test that recently contacted users are excluded"""
        dm_service.recent_sent[456] = datetime.now()
        
        task = dm_service.create_task(
            task_id="test-cd",
            name="Test",
            message_template="Hello!",
            target_users=[123, 456, 789]
        )
        
        assert 456 not in task.target_users
    
    def test_get_stats(self, dm_service):
        """Test getting statistics"""
        dm_service.stats["total_sent"] = 100
        dm_service.stats["total_failed"] = 10
        dm_service.stats["active_tasks"] = 2
        
        stats = dm_service.get_stats()
        
        assert stats["total_sent"] == 100
        assert stats["total_failed"] == 10
        assert stats["active_tasks"] == 2
    
    @pytest.mark.asyncio
    async def test_stop_task(self, dm_service):
        """Test stopping a task"""
        task = dm_service.create_task(
            task_id="test-stop",
            name="Test",
            message_template="Hello!",
            target_users=[1, 2, 3]
        )
        task.status = DMStatus.SENDING
        dm_service.stats["active_tasks"] = 1
        
        result = await dm_service.stop_task("test-stop")
        
        assert result["status"] == "stopped"
        assert task.status == DMStatus.PAUSED
    
    @pytest.mark.asyncio
    async def test_stop_task_not_found(self, dm_service):
        """Test stopping non-existent task"""
        result = await dm_service.stop_task("invalid-id")
        
        assert "error" in result
    
    def test_recently_sent_check(self, dm_service):
        """Test _recently_sent method"""
        user_id = 12345
        
        assert dm_service._recently_sent(user_id) is False
        
        dm_service.recent_sent[user_id] = datetime.now()
        assert dm_service._recently_sent(user_id) is True
        
        dm_service.recent_sent[user_id] = datetime.now() - timedelta(hours=25)
        assert dm_service._recently_sent(user_id) is False


class TestDMTask:
    """Tests for DMTask dataclass"""
    
    def test_task_creation(self):
        """Test DMTask creation"""
        task = DMTask(
            task_id="test-123",
            name="Test Task",
            message_template="Hello!",
            target_users=[1, 2, 3]
        )
        
        assert task.task_id == "test-123"
        assert task.name == "Test Task"
        assert task.sent_count == 0
        assert task.failed_count == 0
        assert task.status == DMStatus.PENDING
    
    def test_task_default_intervals(self):
        """Test default interval values"""
        task = DMTask(
            task_id="test",
            name="Test",
            message_template="",
            target_users=[]
        )
        
        assert task.interval_min == 30.0
        assert task.interval_max == 60.0


class TestFloodProtection:
    """Tests for flood protection logic"""
    
    @pytest.fixture
    def dm_service(self):
        return DMSenderService()
    
    def test_cooldown_period(self, dm_service):
        """Test 24-hour cooldown is enforced"""
        user_id = 12345
        dm_service.recent_sent[user_id] = datetime.now()
        
        task = dm_service.create_task(
            task_id="cd-test",
            name="Test",
            message_template="Hello!",
            target_users=[user_id, 67890]
        )
        
        assert user_id not in task.target_users
        assert 67890 in task.target_users
    
    def test_expired_cooldown(self, dm_service):
        """Test expired cooldown allows user"""
        user_id = 12345
        dm_service.recent_sent[user_id] = datetime.now() - timedelta(hours=25)
        
        task = dm_service.create_task(
            task_id="exp-test",
            name="Test",
            message_template="Hello!",
            target_users=[user_id]
        )
        
        assert user_id in task.target_users
