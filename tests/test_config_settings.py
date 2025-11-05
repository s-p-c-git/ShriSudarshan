# tests/test_config_settings.py
"""
Tests for configuration and settings module.

These tests verify configuration loading and validation.
"""
import os


def test_settings_module_import():
    """Test that settings module can be imported."""
    from src.config import settings
    
    assert settings is not None


def test_settings_has_required_attributes():
    """Test that settings has required configuration attributes."""
    from src.config.settings import Settings
    
    # Verify Settings class exists
    assert Settings is not None
    
    # Create an instance with test env vars already set
    settings_instance = Settings()
    
    # Check for expected attributes
    assert hasattr(settings_instance, "openai_api_key")
    assert hasattr(settings_instance, "premium_model")
    assert hasattr(settings_instance, "standard_model")


def test_settings_api_key_required():
    """Test that API keys are properly configured."""
    from src.config.settings import Settings
    
    settings = Settings()
    
    # API key should be set (from conftest.py)
    assert settings.openai_api_key is not None
    assert len(settings.openai_api_key) > 0


def test_settings_model_names():
    """Test that model names are properly configured."""
    from src.config.settings import Settings
    
    settings = Settings()
    
    # Check model names are set
    assert settings.premium_model is not None
    assert settings.standard_model is not None
    
    # They should be different
    assert settings.premium_model != settings.standard_model


def test_prompts_module():
    """Test that prompts module can be imported and has prompts."""
    from src.config import prompts
    
    assert prompts is not None
    
    # Check for some expected prompts
    assert hasattr(prompts, "FUNDAMENTALS_ANALYST_PROMPT")
    assert hasattr(prompts, "TECHNICAL_ANALYST_PROMPT")
    assert hasattr(prompts, "RISK_MANAGER_PROMPT")


def test_prompts_are_strings():
    """Test that prompts are non-empty strings."""
    from src.config import prompts
    
    # Get all attributes that look like prompts
    prompt_names = [name for name in dir(prompts) if name.endswith("_PROMPT")]
    
    assert len(prompt_names) > 0
    
    for prompt_name in prompt_names:
        prompt = getattr(prompts, prompt_name)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
