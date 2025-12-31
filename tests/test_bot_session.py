"""
Unit tests for BotSession model
"""
import pytest
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import BotSession, BotSessionStatus


class TestBotSession:
    """Tests for BotSession model methods"""
    
    @pytest.fixture
    def bot_session(self):
        """Create a fresh BotSession instance"""
        session = BotSession()
        session.status = BotSessionStatus.ACTIVE
        session.is_active = True
        session.success_rate = 100.0
        session.messages_sent = 0
        session.messages_failed = 0
        session.flood_wait_until = None
        return session
    
    def test_is_available_active(self, bot_session):
        """Test is_available returns True for active session"""
        assert bot_session.is_available() is True
    
    def test_is_available_banned(self, bot_session):
        """Test is_available returns False for banned session"""
        bot_session.status = BotSessionStatus.BANNED
        assert bot_session.is_available() is False
    
    def test_is_available_dead(self, bot_session):
        """Test is_available returns False for dead session"""
        bot_session.status = BotSessionStatus.DEAD
        assert bot_session.is_available() is False
    
    def test_is_available_flood_wait_active(self, bot_session):
        """Test is_available returns False during flood wait"""
        bot_session.flood_wait_until = datetime.now() + timedelta(minutes=5)
        assert bot_session.is_available() is False
    
    def test_is_available_flood_wait_expired(self, bot_session):
        """Test is_available returns True after flood wait expires"""
        bot_session.flood_wait_until = datetime.now() - timedelta(minutes=5)
        assert bot_session.is_available() is True
    
    def test_is_available_low_success_rate(self, bot_session):
        """Test is_available returns False for low success rate"""
        bot_session.success_rate = 20.0
        assert bot_session.is_available() is False
    
    def test_is_available_inactive(self, bot_session):
        """Test is_available returns False for inactive session"""
        bot_session.is_active = False
        assert bot_session.is_available() is False
    
    def test_update_statistics_success(self, bot_session):
        """Test update_statistics for successful message"""
        bot_session.update_statistics(success=True)
        
        assert bot_session.messages_sent == 1
        assert bot_session.messages_failed == 0
        assert bot_session.success_rate == 100.0
    
    def test_update_statistics_failure(self, bot_session):
        """Test update_statistics for failed message"""
        bot_session.update_statistics(success=False)
        
        assert bot_session.messages_sent == 1
        assert bot_session.messages_failed == 1
        assert bot_session.success_rate == 0.0
    
    def test_update_statistics_mixed(self, bot_session):
        """Test update_statistics with mixed results"""
        bot_session.update_statistics(success=True)
        bot_session.update_statistics(success=True)
        bot_session.update_statistics(success=False)
        bot_session.update_statistics(success=True)
        
        assert bot_session.messages_sent == 4
        assert bot_session.messages_failed == 1
        assert bot_session.success_rate == 75.0
    
    def test_update_statistics_updates_last_active(self, bot_session):
        """Test that update_statistics updates last_active timestamp"""
        before = datetime.now()
        bot_session.update_statistics(success=True)
        
        assert bot_session.last_active is not None
        assert bot_session.last_active >= before


class TestBotSessionStatus:
    """Tests for BotSessionStatus constants"""
    
    def test_status_values(self):
        """Test status constant values"""
        assert BotSessionStatus.ACTIVE == "active"
        assert BotSessionStatus.PAUSED == "paused"
        assert BotSessionStatus.FLOODED == "flooded"
        assert BotSessionStatus.BANNED == "banned"
        assert BotSessionStatus.DEAD == "dead"
        assert BotSessionStatus.TESTING == "testing"
