"""
Unit tests for GroupParserService
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.group_parser import GroupParserService, ParserFilter, ParsedUser, ParseJob


class TestGroupParserService:
    """Tests for GroupParserService"""
    
    @pytest.fixture
    def parser_service(self):
        """Create fresh GroupParserService instance"""
        return GroupParserService()
    
    def test_service_initialization(self, parser_service):
        """Test service initializes correctly"""
        assert parser_service.jobs == {}
        assert parser_service.parsed_users_db == {}
        assert parser_service.user_lists == {}
        assert parser_service.stats["total_parsed"] == 0
        assert parser_service.stats["total_groups"] == 0
    
    def test_get_stats(self, parser_service):
        """Test getting statistics"""
        parser_service.stats["total_parsed"] = 100
        parser_service.stats["total_groups"] = 5
        
        stats = parser_service.stats
        
        assert stats["total_parsed"] == 100
        assert stats["total_groups"] == 5
    
    def test_user_lists_storage(self, parser_service):
        """Test user list storage"""
        parser_service.user_lists["test-list"] = [123, 456, 789]
        
        assert "test-list" in parser_service.user_lists
        assert len(parser_service.user_lists["test-list"]) == 3
    
    def test_parsed_users_db(self, parser_service):
        """Test parsed users database"""
        user = ParsedUser(
            user_id=123,
            username="testuser",
            first_name="Test",
            last_name="User",
            phone=None,
            is_bot=False,
            is_premium=True,
            has_photo=True,
            last_seen="recently",
            status="active",
            source_chat_id=1001,
            source_chat_title="Test Group"
        )
        
        parser_service.parsed_users_db[123] = user
        
        assert 123 in parser_service.parsed_users_db
        assert parser_service.parsed_users_db[123].username == "testuser"


class TestParsedUser:
    """Tests for ParsedUser dataclass"""
    
    def test_parsed_user_creation(self):
        """Test ParsedUser creation"""
        user = ParsedUser(
            user_id=12345,
            username="testuser",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            is_bot=False,
            is_premium=True,
            has_photo=True,
            last_seen="recently",
            status="active",
            source_chat_id=1001,
            source_chat_title="Test Group"
        )
        
        assert user.user_id == 12345
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone == "+1234567890"
        assert user.is_premium is True
        assert user.is_bot is False
    
    def test_parsed_user_to_dict(self):
        """Test ParsedUser to_dict method"""
        user = ParsedUser(
            user_id=123,
            username="test",
            first_name="Test",
            last_name=None,
            phone=None,
            is_bot=False,
            is_premium=False,
            has_photo=False,
            last_seen=None,
            status="offline",
            source_chat_id=1,
            source_chat_title="Test"
        )
        
        data = user.to_dict()
        
        assert data["user_id"] == 123
        assert data["username"] == "test"
        assert "parsed_at" in data


class TestParseJob:
    """Tests for ParseJob dataclass"""
    
    def test_parse_job_creation(self):
        """Test ParseJob creation"""
        job = ParseJob(
            job_id="job-123",
            chat_identifier="@testgroup",
            chat_title="Test Group"
        )
        
        assert job.job_id == "job-123"
        assert job.status == "pending"
        assert job.total_members == 0
        assert job.parsed_count == 0
        assert job.users == []
    
    def test_parse_job_with_filters(self):
        """Test ParseJob with filters"""
        job = ParseJob(
            job_id="job-456",
            chat_identifier="@test",
            chat_title="Test",
            filters=[ParserFilter.WITH_USERNAME, ParserFilter.NOT_BOTS]
        )
        
        assert len(job.filters) == 2
        assert ParserFilter.WITH_USERNAME in job.filters


class TestParserFilter:
    """Tests for ParserFilter enum"""
    
    def test_filter_values(self):
        """Test filter enum values"""
        assert ParserFilter.ALL.value == "all"
        assert ParserFilter.WITH_USERNAME.value == "with_username"
        assert ParserFilter.ACTIVE_RECENTLY.value == "active_recently"
        assert ParserFilter.PREMIUM_ONLY.value == "premium_only"
        assert ParserFilter.NOT_BOTS.value == "not_bots"
        assert ParserFilter.WITH_PHONE.value == "with_phone"
        assert ParserFilter.NO_PHOTO.value == "no_photo"
