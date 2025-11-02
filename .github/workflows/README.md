# GitHub Actions CI/CD Workflows

This directory contains automated workflows for continuous integration and deployment.

## Available Workflows

### 1. Test Workflow (`test.yml`)

**Purpose**: Run automated tests on every push and pull request

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does**:
- Runs tests on Python 3.9, 3.10, 3.11, and 3.12
- Executes pytest with code coverage
- Generates coverage reports
- Optionally uploads coverage to Codecov (requires `CODECOV_TOKEN` secret)

**Status Badge**:
```markdown
![Test](https://github.com/s-p-c-git/ShriSudarshan/workflows/Test/badge.svg)
```

### 2. Lint Workflow (`lint.yml`)

**Purpose**: Enforce code quality and style standards

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does**:
- Checks code formatting with Black
- Lints code with Ruff
- Performs type checking with mypy (non-blocking)

**Status Badge**:
```markdown
![Lint](https://github.com/s-p-c-git/ShriSudarshan/workflows/Lint/badge.svg)
```

### 3. Build Workflow (`build.yml`)

**Purpose**: Verify that the package can be built successfully

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does**:
- Builds the package on Python 3.9, 3.10, 3.11, and 3.12
- Creates source distribution and wheel
- Validates package with twine
- Uploads build artifacts (Python 3.12 only)

**Status Badge**:
```markdown
![Build](https://github.com/s-p-c-git/ShriSudarshan/workflows/Build/badge.svg)
```

### 4. Security Workflow (`security.yml`)

**Purpose**: Scan for security vulnerabilities in code and dependencies

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Weekly schedule (Mondays at 00:00 UTC)

**What it does**:
- Scans dependencies for known vulnerabilities using Safety and pip-audit
- Performs static code analysis with CodeQL
- Checks for security issues and code quality problems

**Status Badge**:
```markdown
![Security](https://github.com/s-p-c-git/ShriSudarshan/workflows/Security/badge.svg)
```

## Setting Up Secrets

Some workflows require GitHub secrets to be configured:

### Optional: Codecov Token

If you want to upload coverage reports to Codecov:

1. Sign up at [codecov.io](https://codecov.io)
2. Get your repository token
3. Add it as a secret named `CODECOV_TOKEN` in your GitHub repository settings

## Workflow Status

You can view the status of all workflows in the "Actions" tab of your GitHub repository.

## Local Testing

Before pushing, you can run the same checks locally:

```bash
# Run tests
pytest --verbose --cov=src --cov-report=term-missing

# Check formatting
black --check src/ tests/ examples/

# Lint code
ruff check src/ tests/ examples/

# Type check
mypy src/ --ignore-missing-imports

# Build package
python -m build
twine check dist/*
```

## Troubleshooting

### Tests Failing

- Check the test output in the Actions tab
- Run tests locally with `pytest -v` to reproduce
- Ensure all dependencies are in `requirements.txt`

### Linting Failures

- Run `black src/ tests/ examples/` to auto-format
- Run `ruff check src/ tests/ examples/ --fix` to auto-fix issues
- Review remaining issues manually

### Build Failures

- Ensure `setup.py` is correctly configured
- Check that all package metadata is valid
- Verify that imports work correctly

### Security Issues

- Review the Security tab in GitHub
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Address any high-severity vulnerabilities

## Contributing

When contributing to this project:

1. All workflows must pass before merging
2. Fix any linting issues reported
3. Ensure test coverage doesn't decrease
4. Address security vulnerabilities

## Maintenance

### Updating Actions

GitHub Actions should be kept up to date. Check for updates regularly:

- `actions/checkout` - Currently using v4
- `actions/setup-python` - Currently using v5
- `actions/upload-artifact` - Currently using v4
- `codecov/codecov-action` - Currently using v5
- `github/codeql-action` - Currently using v3

### Adding New Workflows

To add a new workflow:

1. Create a new `.yml` file in `.github/workflows/`
2. Define the trigger events
3. Add the necessary jobs and steps
4. Test locally if possible
5. Document in this README
