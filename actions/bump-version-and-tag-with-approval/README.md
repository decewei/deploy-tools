# Bump Version and Tag with Approval Check Action

This GitHub Action combines approval checking with version bumping and tagging. It's typically used in release workflows to ensure proper approval before creating a release.

## Requirements

### Python Projects

**Python projects MUST use [setuptools-scm](https://setuptools-scm.readthedocs.io/) for version management.**

This action will check for setuptools-scm configuration and **fail if it's not found**. See the [bump-version-and-tag README](../bump-version-and-tag/README.md) for detailed setup instructions.

### Manual Version Management

If you cannot or do not want to use setuptools-scm for Python projects, you must handle version management manually:

1. Manually bump the version in your project files
2. Commit the version bump changes
3. Create and push the git tag manually
4. Then proceed with your release process

**This action will not work for Python projects that don't use setuptools-scm.**

## Usage

```yaml
- name: Bump version and tag with approval check
  uses: decewei/deploy-tools/actions/bump-version-and-tag-with-approval@release
  with:
    app-id: ${{ vars.ACTION_BOT_APP_ID }}
    private-key: ${{ secrets.ACTION_BOT_PRIVATE_KEY }}
    pr-number: ${{ github.event.pull_request.number }}
    repo: ${{ github.repository }}
    require-approvals: 'true'
    tag-prefix: 'v'
    main-branch: 'main'
    release-branch: 'release'
    version-file-type: 'python'
```

## Inputs

Authentication (choose one):
- `token`: GitHub token for git operations
- `app-id` + `private-key`: GitHub App credentials (alternative to token)

Approval settings:
- `pr-number` (optional): Pull request number for approval checks
- `repo` (optional): Repository in owner/name format
- `require-approvals` (optional, default: 'true'): Whether at least one approval is required
- `require-all-reviews` (optional, default: 'true'): Whether all requested reviewers must have approved

Version and tag settings:
- `tag-prefix` (optional, default: 'v'): Prefix for git tags
- `main-branch` (optional, default: 'main'): Main development branch name
- `release-branch` (optional, default: 'release'): Release branch name
- `semantic-version-pattern-major` (optional): Regex pattern for major version bumps
- `semantic-version-pattern-minor` (optional): Regex pattern for minor version bumps
- `version-file-type` (optional, default: 'auto'): Version file type (auto, python, or nodejs)
- `change-path` (optional): Comma-separated paths to consider for semantic versioning

## Outputs

- `continue`: Whether release should proceed (approval check result)
- `tag`: Git tag that was created
- `version`: Bumped version number

## How It Works

1. Configures git authentication (using token or GitHub App)
2. Checks for required approvals on the pull request
3. If approved, calls the [bump-version-and-tag](../bump-version-and-tag) action
4. For Python projects, verifies setuptools-scm configuration
5. Creates git tag (which setuptools-scm uses for versioning)
