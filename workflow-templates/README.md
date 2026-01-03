# Workflow Templates

This directory contains example GitHub Actions workflows demonstrating a complete CI/CD pipeline using the reusable actions from the `actions/` directory.

## Pipeline Overview

The workflow templates implement a 4-stage pipeline:

```
PR created/updated
    ↓
[1] PR Build Check (run tests on pull requests)
    ↓
PR merged to main
    ↓
[2] Staging Deployment (deploy to staging, create release PR)
    ↓
Release PR merged to release branch
    ↓
[3] Release & Production Deploy (version bump, tag, deploy to prod)
    ↓
[4] Rollback (manual option to rollback production)
```

## Workflow Templates

### 1. PR Build Check (`1-1-pr-build-check.yaml`)

**Trigger:** Pull request events

**Purpose:** Validate changes before merging to main

**Actions Used:**
- `dependabot-auto-merge` - Auto-merge dependency updates that pass checks

**Key Features:**
- Runs on every PR created or updated
- Can include custom build and test jobs (reference: `2-build.yaml`)
- Automatically merges dependabot PRs

**Setup:**
```yaml
name: PR build check

on:
  pull_request:

permissions:
  contents: write
  pull-requests: write

jobs:
  build-dev:
    uses: ./.github/workflows/2-build.yaml
    secrets: inherit
    with:
      stage: dev

  dependabot:
    runs-on: ubuntu-latest
    needs: [build-dev]
    steps:
      - name: Auto-merge dependabot PR
        uses: decewei/deploy-tools/actions/dependabot-auto-merge@release
        with:
          app-id: ${{ vars.ACTION_BOT_APP_ID }}
          private-key: ${{ secrets.ACTION_BOT_PRIVATE_KEY }}
```

---

### 2. Staging Deployment (`1-2-staging.yaml`)

**Trigger:** Push to `main` branch or manual trigger

**Purpose:** Deploy validated changes to staging and prepare for release

**Actions Used:**
- `create-release-pr` - Create a PR from main to release branch

**Key Features:**
- Deploys to staging environment
- Creates a release PR for manual review
- Uses concurrency to prevent simultaneous staging/prod changes
- Configurable review team and labels

**Setup:**
```yaml
name: staging

on:
  push:
    branches:
      - main
  workflow_dispatch:

concurrency:
  group: staging-and-prod
  cancel-in-progress: false

permissions:
  contents: write
  pull-requests: write

jobs:
  deploy-staging:
    uses: ./.github/workflows/2-deploy.yaml
    secrets: inherit
    with:
      stage: staging

  create-release-pr:
    runs-on: ubuntu-latest
    needs: deploy-staging
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create release PR
        uses: decewei/deploy-tools/actions/create-release-pr@release
        with:
          app-id: ${{ vars.ACTION_BOT_APP_ID }}
          private-key: ${{ secrets.ACTION_BOT_PRIVATE_KEY }}
          source-branch: 'main'
          target-branch: 'release'
          label: 'release:required-approval'
```

---

### 3. Release & Production Deploy (`1-3-release.yaml`)

**Trigger:** PR merged on `release` branch or manual trigger

**Purpose:** Version bump, create release tag, deploy to production

**Actions Used:**
- `bump-version-and-tag-with-approval` - Verify approval and bump version
- `label-release-pr` - Label PR based on deployment result

**Key Features:**
- Automatic semantic versioning based on commit messages
- Requires approval before proceeding
- Creates git tags for releases
- Deploys approved releases to production
- Supports prerelease versions with `release:candidate` label
- Path-based versioning (optional)

**Semantic Versioning Rules:**
- `BREAKING CHANGE:` or `!:` prefix → major version bump
- `feat:` prefix → minor version bump
- Other commits → patch version bump

**Prerelease Versions:**
- Add `release:candidate` label to release PR for prerelease versioning (e.g., 1.2.3-rc1)

**Setup:**
```yaml
name: Release

on:
  pull_request:
    types: [closed]
    branches:
      - release
  workflow_dispatch:

concurrency:
  group: release
  cancel-in-progress: false

permissions:
  contents: write
  pull-requests: write

jobs:
  version-and-tag:
    runs-on: ubuntu-latest
    outputs:
      continue: ${{ steps.version.outputs.continue }}
      tag: ${{ steps.version.outputs.tag }}
      version: ${{ steps.version.outputs.version }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      
      - name: Bump version and tag with approval check
        id: version
        uses: decewei/deploy-tools/actions/bump-version-and-tag-with-approval@release
        with:
          app-id: ${{ vars.ACTION_BOT_APP_ID }}
          private-key: ${{ secrets.ACTION_BOT_PRIVATE_KEY }}
          pr-number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
          tag-prefix: 'v'
          main-branch: 'main'
          release-branch: 'release'
          semantic-version-pattern-major: '/!:|BREAKING CHANGE:/'
          semantic-version-pattern-minor: '/feat:/'
          version-file-type: 'auto'
          enable-prerelease: ${{ contains(github.event.pull_request.labels.*.name, 'release:candidate') }}
          prerelease-suffix: 'rc'

  deploy-prod:
    if: ${{ needs.version-and-tag.outputs.continue == 'true' }}
    needs: [version-and-tag]
    uses: ./.github/workflows/2-deploy.yaml
    secrets: inherit
    with:
      stage: prod
      ref: ${{ github.event.pull_request.head.sha || github.sha }}

  update-pr-label:
    needs: [version-and-tag, deploy-prod]
    if: ${{ github.event_name == 'pull_request' && needs.version-and-tag.outputs.continue == 'true' && always() }}
    runs-on: ubuntu-latest
    steps:
      - name: Label release PR
        uses: decewei/deploy-tools/actions/label-release-pr@release
        with:
          app-id: ${{ vars.ACTION_BOT_APP_ID }}
          private-key: ${{ secrets.ACTION_BOT_PRIVATE_KEY }}
          pr-number: ${{ github.event.pull_request.number }}
          repo: ${{ github.repository }}
          deploy-result: ${{ needs.deploy-prod.result }}
          released-label: 'release:released'
          failed-label: 'release:failed-to-release'
```

---

### 4. Rollback (`1-4-rollback.yaml`)

**Trigger:** Manual workflow dispatch

**Purpose:** Rollback production to a previous version

**Setup:**
```yaml
name: Rollback

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to (e.g., v1.2.3)'
        required: true
        type: string

# See 1-4-rollback.yaml for complete implementation
```

---

## Implementing in Your Repository

### Step 1: Copy Workflow Files

Copy the workflow YAML files to your repository's `.github/workflows/` directory:

```bash
cp 1-*.yaml your-repo/.github/workflows/
```

### Step 2: Implement Custom Build and Deploy Workflows

You need to create two additional workflows referenced by the templates:

#### `.github/workflows/2-build.yaml`

Create a reusable workflow for building and testing:

```yaml
name: Build

on:
  workflow_call:
    inputs:
      stage:
        required: true
        type: string
        description: 'Build stage (dev, staging, prod)'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and test
        run: |
          # Your build and test commands here
          echo "Building for ${{ inputs.stage }}"
```

#### `.github/workflows/2-deploy.yaml`

Create a reusable workflow for deployment:

```yaml
name: Deploy

on:
  workflow_call:
    inputs:
      stage:
        required: true
        type: string
        description: 'Deployment stage (staging, prod)'
      ref:
        required: false
        type: string
        description: 'Git ref to deploy'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.ref }}
      - name: Deploy
        run: |
          # Your deployment commands here
          echo "Deploying to ${{ inputs.stage }}"
```

### Step 3: Configure Repository Settings

#### Secrets

1. Create a GitHub App with access to your repository (or use an existing one)
2. Generate a private key for the app
3. Add these secrets to your repository:
   - `ACTION_BOT_PRIVATE_KEY` - Private key from your GitHub App

#### Variables

Add these variables to your repository:
- `ACTION_BOT_APP_ID` - Your GitHub App's ID

#### Branch Protection Rules

Configure for the `release` branch:
- Require pull request reviews before merging (e.g., 1 approval)
- Require status checks to pass before merging
- Dismiss stale pull request approvals
- Require branches to be up to date before merging

### Step 4: Configure Version Management

#### For Python Projects

Install and configure setuptools-scm:

```toml
# pyproject.toml
[build-system]
requires = ["setuptools", "setuptools-scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[tool.setuptools-scm]
write_to = "src/_version.py"
```

Then install: `pip install setuptools-scm`

#### For Node.js Projects

Ensure `package.json` has a version field. The action will update it automatically.

### Step 5: Create Label Configuration (Optional)

Create `.github/labels.json` in your repository or use the label sync script from the parent directory to define consistent labels across your organization.

---

## Workflow Execution Examples

### Typical Happy Path

1. **Developer creates PR** → `1-1-pr-build-check` runs (tests pass)
2. **PR is merged to main** → `1-2-staging` runs (deploys to staging, creates release PR)
3. **Release team reviews release PR** → Release PR is approved and merged
4. **Release PR merged to release branch** → `1-3-release` runs (versions, tags, deploys to prod)

### With Dependency Updates

1. **Dependabot creates PR** → `1-1-pr-build-check` runs
2. **Dependabot PR auto-merges** (if it passes) → `1-2-staging` runs
3. **Release PR created** → Proceeds as above

### Emergency Rollback

1. **Manual trigger of `1-4-rollback`** → Production rolls back to specified version

---

## Customization Examples

### Path-Based Versioning

If you have a monorepo with multiple projects, version only specific paths:

```yaml
change-path: 'src/,pyproject.toml'  # Only consider changes in src/ and pyproject.toml
```

### Custom Semantic Version Patterns

Modify the regex patterns to match your commit convention:

```yaml
semantic-version-pattern-major: '/BREAKING|major:/'
semantic-version-pattern-minor: '/feat:|feature:/'
```

### Multiple Review Teams

Create the release PR with specific team review:

```yaml
review-team: '@org/release-team,@org/backend-team'
```

### Conditional Prerelease

Enable prerelease for specific labels:

```yaml
enable-prerelease: ${{ contains(github.event.pull_request.labels.*.name, 'release:candidate') }}
```

---

## Troubleshooting

### Approval Check Failing

- Verify the review team has write access to the repository
- Check that reviewers are actually added as reviewers to the PR
- Ensure `require-all-reviews` setting matches your branch protection rules

### Version Not Bumping

- Check that commits follow semantic versioning patterns (feat:, BREAKING CHANGE:, etc.)
- Verify setuptools-scm (Python) or package.json (Node.js) is properly configured
- Check action logs for detailed version calculation info

### Deployment Failing

- Verify `2-deploy.yaml` exists and is valid
- Check that required secrets and variables are configured
- Review deployment logs in the workflow run

---

## Next Steps

1. Review the [actions README](../README.md) for individual action details
2. Copy and customize these templates for your repository
3. Test the workflow with a real PR and merge
4. Adjust patterns and configurations as needed for your project

For detailed information about each action, see the README files in the `actions/` directory.
