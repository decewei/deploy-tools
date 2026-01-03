# Bump Version and Tag Action

This GitHub Action calculates a semantic version, optionally updates version files, and creates a git tag.

## Requirements

### Python Projects

**Python projects MUST use [setuptools-scm](https://setuptools-scm.readthedocs.io/) for version management.**

This action will check for setuptools-scm configuration and **fail if it's not found**. With setuptools-scm:
- Versions are automatically derived from git tags
- No manual version file updates are needed
- The version is calculated at build/install time

#### Setup for Python Projects

1. Add setuptools-scm to your `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel", "setuptools-scm>=8.0"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package"
dynamic = ["version"]
# ... other fields ...

[tool.setuptools_scm]
version_file = "src/your_package/_version.py"
```

2. Update your package's `__init__.py` to import the version:

```python
try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("your-package")
except PackageNotFoundError:
    try:
        from your_package._version import __version__
    except ImportError:
        __version__ = "0.0.0.dev0"
```

3. Add `_version.py` to your `.gitignore` (it's auto-generated)

#### Error Messages

If setuptools-scm is not configured, the action will fail with:
- `❌ ERROR: setuptools-scm not found in build-system.requires` - Add setuptools-scm to your build requirements
- `❌ ERROR: Version must be listed in "dynamic" field` - Move version to dynamic field in [project] section
- `❌ ERROR: Failed to parse pyproject.toml` - Check TOML syntax

See [setuptools-scm documentation](https://setuptools-scm.readthedocs.io/) for complete setup guide.

### Node.js Projects

For Node.js projects, this action will automatically update the `package.json` version field and commit the change.

## Manual Version Management

If you cannot or do not want to use setuptools-scm for Python projects:

1. Manually bump the version in your project files
2. Commit the version bump changes
3. Create and push the git tag manually:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
4. Proceed with your release process

**This action will not work for Python projects that don't use setuptools-scm.**

## Usage

```yaml
- name: Bump version and tag
  uses: decewei/deploy-tools/actions/bump-version-and-tag@release
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    tag-prefix: 'v'
    main-branch: 'main'
    release-branch: 'release'
    version-file-type: 'python'  # or 'nodejs' or 'auto'
```

## Inputs

- `token` (required): GitHub token for git operations
- `tag-prefix` (optional, default: 'v'): Prefix for git tags
- `main-branch` (optional, default: 'main'): Main development branch name
- `release-branch` (optional, default: 'release'): Release branch name. Set to empty to skip release branch operations
- `semantic-version-pattern-major` (optional): Regex pattern for major version bumps
- `semantic-version-pattern-minor` (optional): Regex pattern for minor version bumps
- `version-file-type` (optional, default: 'auto'): Version file type (auto, python, or nodejs)
- `change-path` (optional): Comma-separated paths to consider for semantic versioning

## How It Works

1. **Calculate semantic version** based on commit history
2. **For Python projects:**
   - Validates setuptools-scm configuration using grep
   - Does NOT modify version files (setuptools-scm derives version from git tags)
3. **For Node.js projects:**
   - Updates `package.json` with new version
   - Verifies HEAD matches main branch
   - Commits the change to main branch
4. **Optionally rebases release branch** onto main (if `release-branch` is not empty)
5. **Creates and pushes git tag** - The tag is applied to current HEAD

### Tag Creation

The tag is always created on the current HEAD after all branch operations complete. For Node.js projects, the commit step ensures HEAD is on the correct commit before tagging.
