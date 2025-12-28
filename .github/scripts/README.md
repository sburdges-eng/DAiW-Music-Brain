# PR Manager

Automated Pull Request Management System

## Overview

The PR Manager automatically processes open pull requests in this repository by:

1. **Attempting to merge** each PR into its target branch (usually `main`)
2. **Successfully merging** PRs without conflicts and deleting their source branches
3. **Creating conflict branches** for PRs that cannot be merged automatically
4. **Commenting on PRs** with detailed conflict information
5. **Reporting summaries** of all operations

## How It Works

### Workflow Trigger

The PR Manager runs automatically:
- **Every 6 hours** via scheduled cron job
- **Manually** via GitHub Actions workflow dispatch

### Process Flow

For each open PR:

#### Case 1: No Conflicts
1. Fetch the latest target branch (e.g., `main`)
2. Attempt merge with source branch
3. If successful:
   - Push the merge to target branch
   - PR is automatically closed by GitHub
   - Delete the source branch

#### Case 2: Conflicts Detected
1. Identify conflicting files
2. Create a new branch: `conflicts/{original-branch-name}`
3. Commit the conflict state to the new branch
4. Push the conflict branch to remote
5. Add a comment to the PR listing:
   - Conflicting files
   - Link to conflict branch
   - Next steps for resolution
6. Leave the original PR open

## Manual Usage

### Run via GitHub Actions

1. Go to **Actions** tab in GitHub
2. Select **PR Manager** workflow
3. Click **Run workflow**
4. Choose branch (usually `main`)
5. Click **Run workflow** button

### Run Locally (Advanced)

```bash
# Prerequisites
pip install PyGithub

# Set environment variables
export GITHUB_TOKEN="your_github_token"
export REPOSITORY="owner/repo-name"

# Run the script
python .github/scripts/pr_manager.py
```

## Safety Features

- **Never force pushes** - All operations use regular git operations
- **Never auto-resolves conflicts** - Conflict states are preserved for human review
- **Atomic operations** - Each PR is processed independently
- **Error handling** - Failures on one PR don't affect others
- **Detailed logging** - All operations are logged for transparency

## Output

### Summary Report

After processing all PRs, the script outputs:

```
================================================================================
PR MANAGEMENT SUMMARY
================================================================================

✓ Successfully Merged and Deleted (2):
  - PR #123: Add new feature
    Branch: feature/new-feature
  - PR #124: Fix bug
    Branch: bugfix/issue-42

⚠️  Moved to Conflict Branch (1):
  - PR #125: Update documentation
    Original: docs/update
    Conflicts: conflicts/docs/update
    Files: README.md, docs/guide.md

================================================================================
```

### PR Comments

For conflicted PRs, an automated comment is added:

```markdown
## ⚠️ Merge Conflicts Detected

This PR cannot be automatically merged due to conflicts in the following files:

- `README.md`
- `docs/guide.md`

A conflict resolution branch has been created: `conflicts/docs/update`

**Next Steps:**
1. Review the conflicts in the `conflicts/docs/update` branch
2. Manually resolve the conflicts
3. Update this PR or create a new one with the resolved changes

The original PR remains open for tracking purposes.
```

## Configuration

### Workflow Schedule

Edit `.github/workflows/pr-manager.yml` to change the schedule:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours (default)
  # Examples:
  # - cron: '0 0 * * *'   # Daily at midnight
  # - cron: '0 */12 * * *' # Every 12 hours
```

### Permissions

The workflow requires:
- `contents: write` - To merge PRs and create branches
- `pull-requests: write` - To comment on PRs

## Troubleshooting

### PR Not Merging

If a PR that should merge isn't merging:
1. Check the workflow logs in Actions tab
2. Verify the PR has no conflicts locally
3. Ensure the target branch is up to date
4. Check branch protection rules

### Conflict Branch Not Created

If conflicts are detected but no branch is created:
1. Check workflow logs for errors
2. Verify repository permissions
3. Ensure the source branch exists
4. Check for naming conflicts with existing branches

### Manual Intervention

To manually resolve a conflicted PR:

```bash
# Checkout the conflict branch
git checkout conflicts/feature-branch-name

# The conflicts are preserved in the branch
# Resolve them manually
git status  # See conflicted files

# After resolving:
git add .
git commit -m "Resolve merge conflicts"
git push origin conflicts/feature-branch-name

# Then create a new PR from the conflict branch
# or update the existing PR to point to the conflict branch
```

## File Structure

```
.github/
├── workflows/
│   └── pr-manager.yml          # GitHub Actions workflow
└── scripts/
    ├── pr_manager.py           # Main PR management script
    └── README.md               # This file
```

## Requirements

- **Python**: 3.9+
- **PyGithub**: Latest version
- **Git**: 2.x+
- **GitHub Token**: With appropriate permissions

## Best Practices

1. **Review conflict branches** before deleting them
2. **Monitor the workflow logs** regularly
3. **Keep PRs small** to reduce conflict likelihood
4. **Update branches frequently** to stay current with target
5. **Use descriptive branch names** for clarity in conflict branches

## Limitations

- Cannot resolve conflicts automatically (by design)
- Requires appropriate GitHub permissions
- Depends on git merge strategy (no-ff)
- Sequential processing (one PR at a time)

## Security

- GitHub token is stored as a secret
- No credentials are logged
- All operations are auditable via git history
- Branch protections are respected

## Support

For issues or questions:
1. Check the workflow logs
2. Review this documentation
3. Open an issue in the repository
