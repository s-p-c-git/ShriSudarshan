# Integration Test Demo

This script demonstrates the security features of Anthropic integration tests without making any actual API calls.

## Purpose

The `demo_integration_tests.py` script shows:
- How API key validation works
- When tests will run vs skip
- Security features (no key exposure)
- CI/CD behavior in GitHub Actions
- Test structure and organization

## Usage

```bash
# Run without API key (shows skip behavior)
python examples/demo_integration_tests.py

# Run with API key (shows detection, but still no API calls)
export ANTHROPIC_API_KEY="sk-ant-your-key"
python examples/demo_integration_tests.py
```

## What It Shows

### 1. API Key Validation
- ✅ Detects if key is present
- ✅ Validates key format (prefix, length)
- ✅ Never exposes actual key value
- ✅ Shows test status (run vs skip)

### 2. Test Markers
- How to use pytest markers
- Running specific test sets
- Excluding integration tests

### 3. CI/CD Behavior
- Two-job workflow structure
- Secret configuration steps
- Cost estimation

### 4. Test Structure
- Test file organization
- Individual test descriptions
- What each test validates

## Safety

This script is completely safe to run:
- ❌ Makes NO API calls
- ❌ Doesn't expose API keys
- ❌ Doesn't modify any files
- ✅ Only demonstrates behavior

## Related Documentation

- [docs/INTEGRATION_TESTING.md](../docs/INTEGRATION_TESTING.md) - Complete integration testing guide
- [tests/test_integration_anthropic.py](../tests/test_integration_anthropic.py) - Actual test implementation
- [.github/workflows/test.yml](../.github/workflows/test.yml) - CI/CD workflow

## Example Output

```
🚀 Anthropic Integration Tests - Security Demo
======================================================================

DEMO: API Key Validation
1. Checking for ANTHROPIC_API_KEY environment variable...
   ❌ API key NOT found
   • Set with: export ANTHROPIC_API_KEY='sk-ant-...'

2. Integration tests status:
   ⏭️  WILL SKIP - No valid API key
   • Tests marked with @pytest.mark.skipif
   • No API calls will be made
```
