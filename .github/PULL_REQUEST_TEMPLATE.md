# Pull Request

## Description
<!-- Provide a brief description of the changes in this PR -->

## Type of Change
<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test additions or improvements

## Related Issue(s)
<!-- Link to the issue(s) this PR addresses -->

Closes #(issue number)

## ⚠️ Code Formatting Checklist (REQUIRED)

**Before submitting this PR, ensure you have:**

- [ ] ✅ Installed pre-commit hooks (`pre-commit install`)
- [ ] ✅ Formatted code with Black (`black src/ tests/ examples/`)
- [ ] ✅ Fixed linting issues with Ruff (`ruff check --fix src/ tests/ examples/`)
- [ ] ✅ Verified formatting passes (`black --check src/ tests/ examples/`)
- [ ] ✅ Verified linting passes (`ruff check src/ tests/ examples/`)

**If you haven't done the above, your PR will fail CI checks and cannot be merged.**

Quick commands to run:
```bash
# Format and fix all issues
black src/ tests/ examples/
ruff check --fix src/ tests/ examples/

# Verify everything passes
black --check src/ tests/ examples/
ruff check src/ tests/ examples/
```

## Testing
<!-- Describe the tests you've run to verify your changes -->

- [ ] All existing tests pass (`pytest tests/`)
- [ ] Added new tests for new functionality
- [ ] Tested manually (if applicable)

**Test output:**
```
# Paste relevant test output here
```

## Documentation
<!-- Check if documentation was updated -->

- [ ] Updated relevant documentation in `docs/`
- [ ] Updated docstrings for modified functions/classes
- [ ] Updated README.md if needed
- [ ] No documentation changes required

## Checklist

- [ ] My code follows the style guidelines of this project (Black + Ruff formatting)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes
<!-- Any additional information, context, or screenshots -->
