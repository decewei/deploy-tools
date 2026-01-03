# Contributing to Deploy Tools

Thank you for your interest in contributing to Deploy Tools! This guide explains how to develop, test, and submit changes to this project.

## Development Workflow

### Understanding the Structure

```text
actions/              # Reusable GitHub Actions
├── action-name/
│   ├── action.yaml   # Action definition and inputs/outputs
│   └── README.md     # Action documentation
workflow-templates/   # Example CI/CD pipeline workflows
├── 1-*.yaml         # Workflow files
└── README.md        # Workflow usage guide
```

### Adding or Modifying Actions

When creating a new action or modifying an existing one:

1. **Update the action.yaml**
   - Define all inputs and outputs clearly
   - Add helpful descriptions for each parameter
   - Set reasonable defaults

2. **Update the README.md**
   - Explain what the action does
   - Document all inputs with type and default values
   - Show example usage in a workflow
   - Document all outputs
   - Explain any requirements or dependencies

3. **Test the action**
   - Test locally with `act` if possible
   - Create a PR and verify it works in the workflow templates
   - Test with both token and GitHub App authentication where applicable

### Modifying Workflow Templates

When updating workflow templates:

1. **Test the workflow** in a branch before merging
2. **Update the workflow template properties file** (`.properties.json`) if changing inputs or outputs
3. **Update the workflow-templates README** with any changes to the workflow logic or requirements
4. **Document the workflow progression** - explain how it fits into the overall pipeline

### Version Management for Actions

When releasing a new version of an action:

1. Update the action version in its directory
2. Use semantic versioning (major.minor.patch)
3. Document changes in the action's README
4. Update references in workflow templates if needed

## Testing Changes

### Local Testing

For bash-heavy actions, you can test locally:

```bash
# Install act to test GitHub Actions locally
# https://github.com/nektos/act

# Run a specific action
act pull_request -l
```

### Testing in a Branch

The best way to test changes is in a feature branch:

1. Create a branch from `main`
2. Make your changes
3. Create a PR referencing your test repository
4. Verify the workflows pass before merging

## Code Style and Standards

- **Bash scripts**: Use `set -e` for error handling, quote variables
- **YAML**: Use 2-space indentation, clear naming for steps and outputs
- **Documentation**: Use clear, concise language with examples

## Documentation Standards

Every action must have:

- A clear, one-line description in the `name` field
- Documented inputs with descriptions and default values
- Documented outputs with descriptions
- A detailed README with:
  - Overview of what the action does
  - Requirements or dependencies
  - Usage example
  - All inputs and outputs reference
  - How it works / implementation notes

## Submitting Changes

1. **Fork the repository** (if you don't have write access)
2. **Create a feature branch** from `main`

```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes**
   - Update action.yaml or workflow templates
   - Update related README files
   - Keep commits focused and descriptive

4. **Test your changes**
   - Verify the workflow templates are valid YAML
   - Test in a real GitHub repository if possible
   - Check that new actions integrate well with existing ones

5. **Create a Pull Request**
   - Include a clear description of your changes
   - Reference any related issues
   - Explain how to test the changes
   - Request review from maintainers

## Pull Request Guidelines

- **One feature/fix per PR** - keep changes focused
- **Clear commit messages** - explain what changed and why
- **Updated documentation** - always update READMEs when changing actions
- **Testing evidence** - show that you've tested your changes
- **No breaking changes** without discussion

## Reporting Issues

When reporting an issue:

1. Check if it's already documented in existing action READMEs
2. Include which action or workflow is affected
3. Provide the relevant workflow snippet if applicable
4. Explain what you expected vs. what happened
5. Include error messages or logs if available

## Common Tasks

### Adding a New Action

```bash
# Create the action directory structure
mkdir -p actions/my-new-action

# Create action.yaml with inputs, outputs, and runs section
# Create README.md with documentation
# Test it by creating a minimal example in workflow templates
```

### Testing a Workflow

The workflow templates in this repo are designed to be copied into your project's `.github/workflows/` directory. To test:

1. Copy the workflow template files
2. Create any required secrets and variables
3. Trigger the workflow manually or via the appropriate event
4. Monitor the workflow run and fix any issues

### Updating Python Script Tools

If modifying `sync-labels.py`:

1. Test locally with appropriate credentials
2. Document any new command-line arguments
3. Update the script's docstring
4. Ensure backward compatibility

## Questions?

If you have questions about contributing:

1. Check the README files for each action
2. Review workflow examples in `workflow-templates/`
3. Open an issue to ask the maintainers
4. Look at recent PRs to see how changes are typically made

## Code of Conduct

Be respectful and constructive in all interactions. We welcome all contributors!
