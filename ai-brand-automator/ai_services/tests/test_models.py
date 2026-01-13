"""
Unit tests for ai_services models.
Tests ChatSession and AIGeneration models.
"""
import pytest
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

from ai_services.models import ChatSession, AIGeneration
from ai_services.tests.factories import (
    ChatSessionFactory,
    AIGenerationFactory,
)


@pytest.mark.django_db
@pytest.mark.unit
class TestChatSessionModel:
    """Tests for ChatSession model"""

    def test_create_chat_session(self, public_tenant):
        """Test creating a chat session with valid data"""
        session = ChatSessionFactory(tenant=public_tenant, title="Test Chat")
        assert session.pk is not None
        assert session.tenant == public_tenant
        assert session.title == "Test Chat"
        assert session.messages == []
        assert session.context == {}

    def test_chat_session_requires_tenant(self):
        """Test that chat session requires a tenant"""
        with pytest.raises(IntegrityError):
            ChatSession.objects.create(
                tenant=None,
                session_id="test-session",
                title="Test",
            )

    def test_chat_session_str_representation(self, public_tenant):
        """Test __str__ method"""
        session = ChatSessionFactory(tenant=public_tenant, title="My Chat")
        assert "My Chat" in str(session)
        assert public_tenant.name in str(session)

    def test_chat_session_str_without_title(self, public_tenant):
        """Test __str__ method when title is empty"""
        session = ChatSessionFactory(tenant=public_tenant, title="")
        assert "Chat Session" in str(session)

    def test_session_id_is_unique(self, public_tenant):
        """Test that session_id must be unique"""
        ChatSessionFactory(tenant=public_tenant, session_id="unique-id")
        with pytest.raises(IntegrityError):
            ChatSession.objects.create(
                tenant=public_tenant,
                session_id="unique-id",  # Duplicate
                title="Another Session",
            )

    def test_add_message_method(self, public_tenant):
        """Test add_message method adds messages correctly"""
        session = ChatSessionFactory(tenant=public_tenant)
        initial_activity = session.last_activity

        session.add_message("user", "Hello, AI!")

        assert len(session.messages) == 1
        assert session.messages[0]["role"] == "user"
        assert session.messages[0]["content"] == "Hello, AI!"
        assert "timestamp" in session.messages[0]
        assert session.last_activity >= initial_activity

    def test_add_message_with_metadata(self, public_tenant):
        """Test add_message with metadata"""
        session = ChatSessionFactory(tenant=public_tenant)
        metadata = {"token_count": 50, "model": "gemini-1.5"}

        session.add_message("assistant", "Hello!", metadata=metadata)

        assert session.messages[0]["metadata"] == metadata

    def test_add_multiple_messages(self, public_tenant):
        """Test adding multiple messages"""
        session = ChatSessionFactory(tenant=public_tenant)

        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        session.add_message("user", "Message 2")

        assert len(session.messages) == 3
        assert session.messages[0]["role"] == "user"
        assert session.messages[1]["role"] == "assistant"
        assert session.messages[2]["role"] == "user"

    def test_messages_default_to_empty_list(self, public_tenant):
        """Test that messages defaults to empty list"""
        session = ChatSession.objects.create(
            tenant=public_tenant,
            session_id="test-defaults",
        )
        assert session.messages == []

    def test_context_default_to_empty_dict(self, public_tenant):
        """Test that context defaults to empty dict"""
        session = ChatSession.objects.create(
            tenant=public_tenant,
            session_id="test-context-defaults",
        )
        assert session.context == {}

    def test_ordering_by_last_activity(self, public_tenant):
        """Test sessions are ordered by last_activity descending"""
        session1 = ChatSessionFactory(
            tenant=public_tenant,
            last_activity=timezone.now() - timedelta(hours=2),
        )
        session2 = ChatSessionFactory(
            tenant=public_tenant,
            last_activity=timezone.now() - timedelta(hours=1),
        )
        session3 = ChatSessionFactory(
            tenant=public_tenant,
            last_activity=timezone.now(),
        )

        sessions = list(ChatSession.objects.all())
        assert sessions[0] == session3
        assert sessions[1] == session2
        assert sessions[2] == session1


@pytest.mark.django_db
@pytest.mark.unit
class TestAIGenerationModel:
    """Tests for AIGeneration model"""

    def test_create_ai_generation(self, public_tenant):
        """Test creating an AI generation record"""
        generation = AIGenerationFactory(
            tenant=public_tenant,
            content_type="brand_strategy",
            prompt="Generate a vision statement",
            response="Your vision is to innovate.",
        )
        assert generation.pk is not None
        assert generation.tenant == public_tenant
        assert generation.content_type == "brand_strategy"

    def test_ai_generation_requires_tenant(self):
        """Test that AI generation requires a tenant"""
        with pytest.raises(IntegrityError):
            AIGeneration.objects.create(
                tenant=None,
                content_type="brand_strategy",
                prompt="Test prompt",
                response="Test response",
            )

    def test_ai_generation_str_representation(self, public_tenant):
        """Test __str__ method"""
        generation = AIGenerationFactory(
            tenant=public_tenant,
            content_type="brand_identity",
        )
        result = str(generation)
        assert "brand_identity" in result
        assert public_tenant.name in result

    def test_content_type_choices(self, public_tenant):
        """Test valid content_type choices"""
        valid_types = ["brand_strategy", "brand_identity", "content", "analysis"]
        for content_type in valid_types:
            generation = AIGenerationFactory(
                tenant=public_tenant,
                content_type=content_type,
            )
            assert generation.content_type == content_type

    def test_tokens_used_defaults_to_zero(self, public_tenant):
        """Test tokens_used defaults to 0"""
        generation = AIGeneration.objects.create(
            tenant=public_tenant,
            content_type="brand_strategy",
            prompt="Test",
            response="Response",
        )
        assert generation.tokens_used == 0

    def test_model_used_default(self, public_tenant):
        """Test model_used has default value"""
        generation = AIGeneration.objects.create(
            tenant=public_tenant,
            content_type="brand_strategy",
            prompt="Test",
            response="Response",
        )
        assert generation.model_used == "gemini-2.0-flash-exp"

    def test_processing_time_defaults_to_zero(self, public_tenant):
        """Test processing_time defaults to 0.0"""
        generation = AIGeneration.objects.create(
            tenant=public_tenant,
            content_type="brand_strategy",
            prompt="Test",
            response="Response",
        )
        assert generation.processing_time == 0.0

    def test_ordering_by_created_at(self, public_tenant):
        """Test generations are ordered by created_at descending"""
        gen1 = AIGenerationFactory(
            tenant=public_tenant,
            created_at=timezone.now() - timedelta(hours=2),
        )
        gen2 = AIGenerationFactory(
            tenant=public_tenant,
            created_at=timezone.now() - timedelta(hours=1),
        )
        gen3 = AIGenerationFactory(
            tenant=public_tenant,
            created_at=timezone.now(),
        )

        generations = list(AIGeneration.objects.all())
        assert generations[0] == gen3
        assert generations[1] == gen2
        assert generations[2] == gen1

    def test_long_prompt_and_response(self, public_tenant):
        """Test that long prompts and responses are handled"""
        long_prompt = "A" * 10000
        long_response = "B" * 10000

        generation = AIGeneration.objects.create(
            tenant=public_tenant,
            content_type="content",
            prompt=long_prompt,
            response=long_response,
        )

        generation.refresh_from_db()
        assert len(generation.prompt) == 10000
        assert len(generation.response) == 10000
