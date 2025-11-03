# Integration Testing with Anthropic API

This document explains how to run and configure integration tests for the Anthropic API in Project Shri Sudarshan.

## Overview

Integration tests validate real-world API interactions with Anthropic's Claude models. These tests:

- **Run conditionally**: Only execute when a valid API key is provided
- **Are secure**: Never log or expose API keys
- **Execute once**: Designed for single successful runs to minimize API costs
- **Skip gracefully**: Automatically skip if no API key is available

## Security Principles

### ✅ Safe Practices
- API keys loaded from environment variables only
- No hardcoded keys in any source files
- No logging or printing of API key values
- Tests skip automatically if key is not available
- GitHub Actions uses encrypted repository secrets

### ❌ Unsafe Practices (Never Do)
- Never commit API keys to git
- Never hardcode keys in test files
- Never print/log API key values
- Never push `.env` files with real keys

## Running Integration Tests Locally

### Prerequisites

1. **Valid Anthropic API Key**: Obtain from [Anthropic Console](https://console.anthropic.com/)
2. **Python 3.9+** installed
3. **Dependencies installed**: `pip install -r requirements.txt`

### Setup

1. Create a `.env` file (or export environment variable):
   ```bash
   # .env file
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

2. Or export directly in your shell:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"
   ```

### Run Integration Tests

```bash
# Run only Anthropic integration tests
pytest -m anthropic

# Run specific test file
pytest tests/test_integration_anthropic.py

# Run with verbose output
pytest -v -m anthropic

# Run all integration tests (future-proof)
pytest -m integration
```

### Run Unit Tests (Exclude Integration)

```bash
# Run only unit tests, skip all integration tests
pytest -m "not integration"

# This is the default behavior in CI
pytest --cov=src -m "not integration"
```

### Expected Output

**When API key is available:**
```
tests/test_integration_anthropic.py::TestAnthropicIntegration::test_anthropic_llm_creation PASSED
tests/test_integration_anthropic.py::TestAnthropicIntegration::test_anthropic_simple_invocation PASSED
tests/test_integration_anthropic.py::TestAnthropicIntegration::test_anthropic_agent_workflow PASSED
```

**When API key is NOT available:**
```
tests/test_integration_anthropic.py::TestAnthropicIntegration::test_anthropic_llm_creation SKIPPED
Reason: ANTHROPIC_API_KEY not set or invalid
```

## Running in CI/CD (GitHub Actions)

### Setup Repository Secret

1. Navigate to your GitHub repository
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: Your Anthropic API key (e.g., `sk-ant-api03-...`)
6. Click **Add secret**

### Workflow Configuration

The `.github/workflows/test.yml` includes two jobs:

#### 1. Unit Tests Job
- Runs on all Python versions (3.9, 3.10, 3.11, 3.12)
- Excludes integration tests: `pytest -m "not integration"`
- Runs on every push/PR
- Fast execution, no external API calls

#### 2. Integration Tests Job
- Runs only on Python 3.12 (to avoid multiple API calls)
- Runs only when `ANTHROPIC_API_KEY` secret exists
- Executes: `pytest -m anthropic`
- Securely passes API key via environment variable

### Workflow Behavior

**With API key configured:**
```yaml
- name: Run Anthropic integration tests
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: pytest --verbose -m anthropic
```

**Without API key:**
- Integration tests job skips with informative message
- Unit tests still run successfully
- No test failures due to missing API key

## Test Structure

### Test File: `tests/test_integration_anthropic.py`

#### Test Classes

1. **TestAnthropicIntegration**
   - `test_anthropic_llm_creation`: Validates LLM factory creates ChatAnthropic
   - `test_anthropic_simple_invocation`: Single API call with simple prompt
   - `test_anthropic_agent_workflow`: Simulates realistic agent interaction

2. **TestAnthropicSettings**
   - `test_anthropic_settings_validation`: Configuration validation
   - `test_anthropic_model_selection`: Model selection logic

3. **TestAnthropicSkipConditions**
   - `test_skip_detection_functions`: Validates skip logic (always runs)

### Test Markers

```python
# Mark individual tests
@pytest.mark.integration
@pytest.mark.anthropic
async def test_anthropic_simple_invocation():
    ...

# Mark entire class
pytestmark = [pytest.mark.integration, pytest.mark.anthropic]
```

## API Key Validation

Integration tests use smart validation:

```python
def is_anthropic_available() -> bool:
    """Check if API key is available and appears valid."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return False
    # Validate format without exposing key
    return key.startswith("sk-ant-") and len(key) > 20
```

This checks:
- ✅ Key exists in environment
- ✅ Key starts with `sk-ant-` prefix
- ✅ Key has reasonable length (>20 chars)
- ❌ Does NOT expose actual key value

## Cost Considerations

Integration tests are designed to minimize API costs:

1. **Single execution**: Run once per test session
2. **Short prompts**: Use minimal tokens for validation
3. **Python 3.12 only**: CI runs on single Python version
4. **Skip by default**: Must explicitly run with `-m anthropic`
5. **No loops**: No repeated API calls in tests

### Estimated Costs (Claude Sonnet)

- **Per test run**: ~$0.01 (3 API calls, ~1000 tokens total)
- **Per CI run**: ~$0.01 (only on Python 3.12)
- **Monthly CI usage**: ~$0.30 (assuming 30 runs/month)

## Troubleshooting

### Test Skipped: API Key Not Set

**Problem**: Tests show "SKIPPED" status

**Solution**: Set `ANTHROPIC_API_KEY` environment variable
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"
pytest -m anthropic
```

### Test Failed: Authentication Error

**Problem**: Tests fail with 401 Unauthorized

**Solution**: Verify API key is correct
1. Check key starts with `sk-ant-api03-`
2. Verify key is active in Anthropic Console
3. Ensure no extra spaces/newlines in key

### Test Failed: Rate Limit

**Problem**: Tests fail with 429 rate limit error

**Solution**: Wait and retry
- Anthropic has rate limits
- Wait a few minutes before retrying
- Consider running less frequently

### CI Tests Not Running

**Problem**: Integration tests don't run in GitHub Actions

**Solution**: Verify repository secret is set
1. Check **Settings** → **Secrets** → **Actions**
2. Ensure `ANTHROPIC_API_KEY` exists
3. Check secret name matches exactly (case-sensitive)

## Best Practices

### For Development

1. **Use separate API keys**: Dev keys separate from production
2. **Run locally first**: Test before pushing to CI
3. **Check costs**: Monitor Anthropic usage dashboard
4. **Skip in .gitignore**: Ensure `.env` is gitignored

### For CI/CD

1. **Rotate keys regularly**: Update secrets periodically
2. **Monitor usage**: Check Anthropic billing dashboard
3. **Limit runs**: Don't run integration tests on every commit
4. **Use branch protection**: Require integration tests only for main/develop

### For Contributors

1. **Document key setup**: Clear instructions in PR/README
2. **Never share keys**: Don't post keys in issues/PRs
3. **Test locally**: Validate before requesting CI runs
4. **Skip if unsure**: Use `-m "not integration"` by default

## Future Enhancements

Potential improvements for integration testing:

1. **Test fixtures**: Reusable API response fixtures
2. **Mocking layer**: Record/replay API responses
3. **Multiple models**: Test different Claude versions
4. **Performance metrics**: Track latency and token usage
5. **Error scenarios**: Test rate limits, timeouts
6. **Workflow tests**: Full multi-agent workflow validation

## Related Documentation

- [TESTING.md](../docs/TESTING.md): General testing documentation
- [README.md](../README.md): Project overview and setup
- [.env.example](../.env.example): Environment variable template

## Support

For issues with integration tests:

1. Check this documentation first
2. Verify API key configuration
3. Review test output for specific errors
4. Check Anthropic status page
5. Open GitHub issue with details (never include API key!)

---

**Remember**: Always keep API keys secure. Never commit them to git or share them publicly.
