# Deploy Tools

A collection of reusable GitHub Actions and workflow templates for implementing a comprehensive CI/CD pipeline with version management, automated testing, staging, and production deployments.

## Overview

This repository provides:

- **Reusable GitHub Actions** in the `actions/` directory for common CI/CD tasks
- **Workflow Templates** in the `workflow-templates/` directory showing best-practice pipeline patterns
- **Configuration** for managing labels and repository settings

## What's Inside

### Actions

The `actions/` directory contains the following reusable GitHub Actions:

| Action | Purpose |
| --- | --- |
| `bump-version-and-tag` | Calculate semantic version based on commit messages and create git tags |
| `bump-version-and-tag-with-approval` | Combine approval checking with version bumping and tagging |
| `check-release-approval` | Validate that a release PR is approved by all requested reviewers |
| `configure-git-auth` | Configure git authentication using token or GitHub App credentials |
| `create-release-pr` | Create or update a release PR from source to target branch |
| `dependabot-auto-merge` | Automatically merge dependabot PRs that pass checks |
| `label-release-pr` | Apply labels to release PRs based on deployment results |

Each action has its own `action.yaml` configuration and README with detailed documentation.

### Workflow Templates

The `workflow-templates/` directory contains example workflows demonstrating how to use these actions:

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `1-1-pr-build-check` | Pull request | Build and test PR changes |
| `1-2-staging` | Push to main | Deploy to staging environment |
| `1-3-release` | PR merged on release branch | Create release and deploy to production |
| `1-4-rollback` | Manual trigger | Rollback production to previous version |

See the [workflow-templates README](workflow-templates/README.md) for detailed examples of how to use these actions in your pipeline.

## Getting Started

### For Repository Maintainers

1. Review the [workflow templates](workflow-templates/README.md) to understand the recommended CI/CD pipeline structure
2. Adapt the workflow files to your repository's needs
3. Configure repository secrets and variables (see below)
4. Copy the workflow files to your `.github/workflows/` directory

### Required Repository Configuration

#### Secrets

- `ACTION_BOT_PRIVATE_KEY`: Private key for the GitHub App used by actions

#### Variables

- `ACTION_BOT_APP_ID`: App ID for the GitHub App used by actions

#### Branch Protection Rules (Recommended)

For the release workflow to work properly, configure:

- **Release branch** (`release`): Require PR reviews and status checks before merging
- **Main branch** (`main`): Require status checks to pass before merging

### Version Management

#### Python Projects

This toolset uses **[setuptools-scm](https://setuptools-scm.readthedocs.io/)** for automatic version management from git tags:

1. Install setuptools-scm: `pip install setuptools-scm`
2. Configure in `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools", "setuptools-scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools-scm]
write_to = "src/_version.py"
```

#### Node.js Projects

For Node.js projects, ensure `package.json` exists with a version field that can be updated automatically.

## Configuration Files

- `repo-config.json`: Repository list and label configurations
- `label-config.json`: GitHub label definitions and colors
- `sync-labels.py`: Python script to synchronize labels across repositories

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

