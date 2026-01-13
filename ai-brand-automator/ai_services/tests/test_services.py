"""
Unit tests for ai_services.services module.
Tests GeminiAIService with mocked Gemini API.
"""
import pytest
from unittest.mock import patch, MagicMock

from ai_services.services import GeminiAIService
from ai_services.models import AIGeneration


@pytest.mark.django_db
@pytest.mark.unit
class TestGeminiAIServiceInit:
    """Tests for GeminiAIService initialization"""

    @patch("ai_services.services.genai")
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-api-key"})
    def test_init_with_api_key(self, mock_genai):
        """Test initialization with valid API key"""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        service = GeminiAIService()

        mock_genai.configure.assert_called_once_with(api_key="test-api-key")
        assert service.model is not None

    @patch("ai_services.services.genai")
    @patch.dict("os.environ", {"GOOGLE_API_KEY": ""}, clear=True)
    def test_init_without_api_key(self, mock_genai):
        """Test initialization without API key (fallback mode)"""
        # Mock settings to not have API key either
        with patch("ai_services.services.settings") as mock_settings:
            mock_settings.GOOGLE_API_KEY = None

            service = GeminiAIService()

            # Model should be None in fallback mode
            assert service.model is None


@pytest.mark.django_db
@pytest.mark.unit
class TestGenerateBrandStrategy:
    """Tests for generate_brand_strategy method"""

    def test_fallback_response_without_model(self):
        """Test fallback response when model is not configured"""
        # Simulate missing API key so service initializes in fallback mode
        with patch.dict("os.environ", {"GOOGLE_API_KEY": ""}, clear=False):
            with patch("ai_services.services.settings") as mock_settings:
                mock_settings.GOOGLE_API_KEY = None

                service = GeminiAIService()

                # Sanity-check that we're in fallback mode
                assert service.model is None

                company_data = {
                    "name": "Test Company",
                    "industry": "Technology",
                    "target_audience": "Developers",
                    "core_problem": "Complex deployments",
                    "brand_voice": "professional",
                }

                result = service.generate_brand_strategy(company_data)

                assert "vision_statement" in result
                assert "mission_statement" in result
                assert "values" in result
                assert "positioning_statement" in result
                # Fallback should include industry in response
                assert "Technology" in result["vision_statement"]

    @patch("ai_services.services.genai")
    def test_successful_api_response(self, mock_genai, public_tenant):
        """Test successful Gemini API response"""
        mock_response = MagicMock()
        mock_response.text = """
        Vision Statement: To be the global leader in innovative technology.

        Mission Statement: We deliver cutting-edge solutions.

        Core Values:
        - Innovation
        - Excellence
        - Integrity

        Positioning Statement: The trusted partner for tech innovation.
        """

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = mock_model
            service.api_key = "test-key"
            service.model_name = "gemini-1.5-flash"

            company_data = {
                "tenant": public_tenant,
                "name": "Test Company",
                "industry": "Technology",
                "target_audience": "Developers",
                "core_problem": "Complex deployments",
                "brand_voice": "professional",
            }

            result = service.generate_brand_strategy(company_data)

            assert "vision_statement" in result
            assert "mission_statement" in result
            mock_model.generate_content.assert_called_once()

    def test_logs_ai_generation(self, public_tenant):
        """Test that AI generation is logged to database"""
        initial_count = AIGeneration.objects.count()

        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            company_data = {
                "tenant": public_tenant,
                "name": "Test Company",
                "industry": "Technology",
                "target_audience": "Developers",
                "core_problem": "Complex deployments",
                "brand_voice": "professional",
            }

            service.generate_brand_strategy(company_data)

            assert AIGeneration.objects.count() == initial_count + 1
            generation = AIGeneration.objects.latest("created_at")
            assert generation.content_type == "brand_strategy"
            assert generation.tenant == public_tenant

    @patch("ai_services.services.genai")
    def test_handles_api_exception(self, mock_genai, public_tenant):
        """Test graceful handling of API exceptions"""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = mock_model
            service.api_key = "test-key"
            service.model_name = "gemini-1.5-flash"

            company_data = {
                "tenant": public_tenant,
                "name": "Test Company",
                "industry": "Technology",
                "target_audience": "Developers",
                "core_problem": "Complex deployments",
                "brand_voice": "professional",
            }

            # Should not raise, should return fallback
            result = service.generate_brand_strategy(company_data)

            assert "vision_statement" in result
            assert "mission_statement" in result


@pytest.mark.django_db
@pytest.mark.unit
class TestGenerateBrandIdentity:
    """Tests for generate_brand_identity method"""

    def test_fallback_response_without_model(self, public_tenant):
        """Test fallback response when model is not configured"""
        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            company_data = {
                "tenant": public_tenant,
                "name": "Test Company",
                "industry": "Technology",
                "brand_voice": "professional",
                "target_audience": "Developers",
            }

            result = service.generate_brand_identity(company_data)

            assert "color_palette_desc" in result
            assert "font_recommendations" in result
            assert "messaging_guide" in result
            # Should contain color codes
            assert "#" in result["color_palette_desc"]

    @patch("ai_services.services.genai")
    def test_successful_api_response(self, mock_genai, public_tenant):
        """Test successful Gemini API response for brand identity"""
        mock_response = MagicMock()
        mock_response.text = """
        Color Palette: Primary blue #0066CC, secondary white #FFFFFF

        Typography: Montserrat for headings, Open Sans for body

        Messaging Guide: Use professional and clear language
        """

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = mock_model
            service.api_key = "test-key"
            service.model_name = "gemini-1.5-flash"

            company_data = {
                "tenant": public_tenant,
                "name": "Test Company",
                "industry": "Technology",
                "brand_voice": "professional",
                "target_audience": "Developers",
            }

            result = service.generate_brand_identity(company_data)

            assert "color_palette_desc" in result
            mock_model.generate_content.assert_called_once()

    def test_logs_brand_identity_generation(self, public_tenant):
        """Test that brand identity generation is logged"""
        initial_count = AIGeneration.objects.filter(
            content_type="brand_identity"
        ).count()

        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            company_data = {
                "tenant": public_tenant,
                "name": "Test Company",
                "industry": "Technology",
                "brand_voice": "professional",
                "target_audience": "Developers",
            }

            service.generate_brand_identity(company_data)

            new_count = AIGeneration.objects.filter(
                content_type="brand_identity"
            ).count()
            assert new_count == initial_count + 1


@pytest.mark.django_db
@pytest.mark.unit
class TestChatWithBrandContext:
    """Tests for chat_with_brand_context method"""

    def test_vision_keyword_response(self, public_tenant):
        """Test response when message contains 'vision'"""
        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            context = {
                "tenant": public_tenant,
                "company": {"name": "Test Co", "industry": "Technology"},
            }

            result = service.chat_with_brand_context(
                "Help me with my vision statement", context
            )

            assert "vision" in result.lower()

    def test_mission_keyword_response(self, public_tenant):
        """Test response when message contains 'mission'"""
        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            context = {
                "tenant": public_tenant,
                "company": {"name": "Test Co", "industry": "Technology"},
            }

            result = service.chat_with_brand_context(
                "What should my mission be?", context
            )

            assert "mission" in result.lower()

    def test_values_keyword_response(self, public_tenant):
        """Test response when message contains 'values'"""
        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            context = {
                "tenant": public_tenant,
                "company": {"name": "Test Co", "industry": "Technology"},
            }

            result = service.chat_with_brand_context(
                "Help define my company values", context
            )

            assert "values" in result.lower()

    def test_generic_response(self, public_tenant):
        """Test generic response for unrecognized keywords"""
        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            context = {
                "tenant": public_tenant,
                "company": {"name": "Test Co", "industry": "Technology"},
            }

            result = service.chat_with_brand_context("Hello there!", context)

            assert "brand strategy" in result.lower()


@pytest.mark.django_db
@pytest.mark.unit
class TestPromptBuilding:
    """Tests for private prompt building methods"""

    def test_brand_strategy_prompt_contains_company_data(self, public_tenant):
        """Test that brand strategy prompt includes company information"""
        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            company_data = {
                "name": "Acme Corp",
                "industry": "Manufacturing",
                "target_audience": "Industrial buyers",
                "core_problem": "Supply chain inefficiency",
                "brand_voice": "authoritative",
            }

            prompt = service._build_brand_strategy_prompt(company_data)

            assert "Acme Corp" in prompt
            assert "Manufacturing" in prompt
            assert "Industrial buyers" in prompt

    def test_brand_identity_prompt_contains_company_data(self, public_tenant):
        """Test that brand identity prompt includes company information"""
        with patch.object(GeminiAIService, "__init__", lambda self: None):
            service = GeminiAIService()
            service.model = None
            service.api_key = None

            company_data = {
                "name": "Design Co",
                "industry": "Creative",
                "brand_voice": "playful",
                "target_audience": "Creative professionals",
            }

            prompt = service._build_brand_identity_prompt(company_data)

            assert "Design Co" in prompt
            assert "Creative" in prompt
