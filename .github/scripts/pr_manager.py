#!/usr/bin/env python3
"""
PR Manager Script

This script manages open pull requests by:
1. Attempting to merge PRs without conflicts
2. Creating conflict branches for PRs that cannot be merged
3. Commenting on PRs with conflict information
4. Deleting merged branches

Usage:
    GITHUB_TOKEN=<token> REPOSITORY=owner/repo python pr_manager.py
"""

import os
import sys
import subprocess
from typing import List, Dict, Tuple
from github import Github, GithubException


class PRManager:
    def __init__(self, token: str, repository: str):
        """Initialize PR Manager with GitHub credentials."""
        self.github = Github(token)
        self.repo = self.github.get_repo(repository)
        self.token = token
        self.successfully_merged = []
        self.conflict_branches = []
        
    def run_git_command(self, cmd: List[str], check=True) -> Tuple[int, str, str]:
        """Run a git command and return (returncode, stdout, stderr)."""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if check and result.returncode != 0:
            print(f"Command failed: {' '.join(cmd)}")
            print(f"Error: {result.stderr}")
            
        return result.returncode, result.stdout, result.stderr
    
    def get_open_prs(self):
        """Get all open pull requests."""
        return list(self.repo.get_pulls(state='open'))
    
    def identify_target_branch(self, pr) -> str:
        """Identify the target branch for a PR (usually main or master)."""
        return pr.base.ref
    
    def fetch_branches(self):
        """Fetch all remote branches."""
        print("Fetching all remote branches...")
        self.run_git_command(['git', 'fetch', '--all'])
        self.run_git_command(['git', 'fetch', 'origin', '--prune'])
    
    def attempt_merge(self, pr) -> Tuple[bool, List[str]]:
        """
        Attempt to merge a PR branch into its target branch.
        
        Returns:
            (success: bool, conflicts: List[str])
        """
        target_branch = self.identify_target_branch(pr)
        source_branch = pr.head.ref
        
        print(f"\n{'='*80}")
        print(f"Processing PR #{pr.number}: {pr.title}")
        print(f"  Source: {source_branch}")
        print(f"  Target: {target_branch}")
        print(f"{'='*80}")
        
        # Checkout target branch
        print(f"Checking out target branch '{target_branch}'...")
        returncode, _, _ = self.run_git_command(
            ['git', 'checkout', target_branch],
            check=False
        )
        if returncode != 0:
            print(f"Warning: Could not checkout {target_branch}, trying origin/{target_branch}")
            self.run_git_command(['git', 'checkout', '-b', target_branch, f'origin/{target_branch}'])
        
        # Update target branch
        print(f"Pulling latest changes from '{target_branch}'...")
        self.run_git_command(['git', 'pull', 'origin', target_branch])
        
        # Attempt merge
        print(f"Attempting to merge '{source_branch}' into '{target_branch}'...")
        returncode, stdout, stderr = self.run_git_command(
            ['git', 'merge', '--no-ff', '--no-commit', f'origin/{source_branch}'],
            check=False
        )
        
        if returncode == 0:
            # Check if there are any changes to commit
            status_code, status_out, _ = self.run_git_command(
                ['git', 'status', '--porcelain'],
                check=False
            )
            
            if status_out.strip():
                # Commit the merge
                print("Merge successful! Committing...")
                self.run_git_command([
                    'git', 'commit', '-m',
                    f"Merge PR #{pr.number}: {pr.title}"
                ])
                return True, []
            else:
                print("No changes to merge (already up to date)")
                # Abort the merge attempt
                self.run_git_command(['git', 'merge', '--abort'], check=False)
                return True, []
        else:
            # Check for conflicts
            print("Merge has conflicts!")
            conflicts = self.get_conflicting_files()
            
            # Abort the merge
            print("Aborting merge...")
            self.run_git_command(['git', 'merge', '--abort'], check=False)
            
            return False, conflicts
    
    def get_conflicting_files(self) -> List[str]:
        """Get list of files with merge conflicts."""
        _, stdout, _ = self.run_git_command(
            ['git', 'diff', '--name-only', '--diff-filter=U'],
            check=False
        )
        
        conflicts = [f.strip() for f in stdout.split('\n') if f.strip()]
        return conflicts
    
    def create_conflict_branch(self, pr, conflicts: List[str]) -> bool:
        """
        Create a branch with the conflict state.
        
        Args:
            pr: GitHub PR object
            conflicts: List of conflicting files
            
        Returns:
            bool: Success status
        """
        source_branch = pr.head.ref
        target_branch = self.identify_target_branch(pr)
        conflict_branch = f"conflicts/{source_branch}"
        
        print(f"\nCreating conflict branch '{conflict_branch}'...")
        
        # Checkout target branch
        self.run_git_command(['git', 'checkout', target_branch])
        self.run_git_command(['git', 'pull', 'origin', target_branch])
        
        # Create new conflict branch from target
        print(f"Creating branch '{conflict_branch}'...")
        # Delete if exists
        self.run_git_command(['git', 'branch', '-D', conflict_branch], check=False)
        self.run_git_command(['git', 'checkout', '-b', conflict_branch])
        
        # Attempt merge to get conflict state
        print(f"Merging '{source_branch}' to capture conflict state...")
        self.run_git_command(
            ['git', 'merge', '--no-commit', f'origin/{source_branch}'],
            check=False
        )
        
        # Add conflicted files
        print("Adding conflicted files...")
        self.run_git_command(['git', 'add', '.'])
        
        # Commit the conflict state
        print("Committing conflict state...")
        commit_msg = f"Conflict state for PR #{pr.number}: {pr.title}\n\nConflicting files:\n"
        commit_msg += '\n'.join(f"  - {f}" for f in conflicts)
        
        self.run_git_command(['git', 'commit', '-m', commit_msg], check=False)
        
        # Push the conflict branch
        print(f"Pushing '{conflict_branch}' to remote...")
        returncode, _, stderr = self.run_git_command(
            ['git', 'push', '-u', 'origin', conflict_branch],
            check=False
        )
        
        if returncode == 0:
            print(f"✓ Conflict branch '{conflict_branch}' created and pushed")
            return True
        else:
            print(f"✗ Failed to push conflict branch: {stderr}")
            return False
    
    def comment_on_pr(self, pr, conflicts: List[str], conflict_branch: str):
        """Add a comment to the PR listing conflicting files."""
        comment = f"""## ⚠️ Merge Conflicts Detected

This PR cannot be automatically merged due to conflicts in the following files:

"""
        for conflict in conflicts:
            comment += f"- `{conflict}`\n"
        
        comment += f"""
A conflict resolution branch has been created: `{conflict_branch}`

**Next Steps:**
1. Review the conflicts in the `{conflict_branch}` branch
2. Manually resolve the conflicts
3. Update this PR or create a new one with the resolved changes

The original PR remains open for tracking purposes.
"""
        
        try:
            pr.create_issue_comment(comment)
            print(f"✓ Comment added to PR #{pr.number}")
        except GithubException as e:
            print(f"✗ Failed to comment on PR #{pr.number}: {e}")
    
    def delete_branch(self, branch_name: str) -> bool:
        """Delete a remote branch."""
        print(f"Deleting branch '{branch_name}'...")
        
        returncode, _, stderr = self.run_git_command(
            ['git', 'push', 'origin', '--delete', branch_name],
            check=False
        )
        
        if returncode == 0:
            print(f"✓ Branch '{branch_name}' deleted")
            return True
        else:
            print(f"✗ Failed to delete branch '{branch_name}': {stderr}")
            return False
    
    def merge_pr(self, pr) -> bool:
        """Merge a PR via GitHub API."""
        try:
            target_branch = self.identify_target_branch(pr)
            
            # Push the merge we created
            print(f"Pushing merge to '{target_branch}'...")
            returncode, _, stderr = self.run_git_command(
                ['git', 'push', 'origin', target_branch],
                check=False
            )
            
            if returncode != 0:
                print(f"✗ Failed to push merge: {stderr}")
                return False
            
            # Close the PR as merged via API
            print(f"Closing PR #{pr.number} as merged...")
            # Note: The PR should be automatically closed by GitHub when we push the merge
            # But we can also explicitly mark it
            
            print(f"✓ PR #{pr.number} merged successfully")
            return True
            
        except GithubException as e:
            print(f"✗ Failed to merge PR #{pr.number}: {e}")
            return False
    
    def process_pr(self, pr):
        """Process a single PR."""
        success, conflicts = self.attempt_merge(pr)
        
        if success:
            # Merge succeeded
            print(f"\n✓ PR #{pr.number} can be merged without conflicts")
            
            # Complete the merge
            if self.merge_pr(pr):
                self.successfully_merged.append({
                    'number': pr.number,
                    'title': pr.title,
                    'branch': pr.head.ref
                })
                
                # Delete the source branch
                self.delete_branch(pr.head.ref)
            else:
                # Reset if merge failed
                self.run_git_command(['git', 'reset', '--hard', 'HEAD~1'], check=False)
        else:
            # Merge has conflicts
            print(f"\n✗ PR #{pr.number} has conflicts")
            
            # Create conflict branch
            conflict_branch = f"conflicts/{pr.head.ref}"
            if self.create_conflict_branch(pr, conflicts):
                # Comment on PR
                self.comment_on_pr(pr, conflicts, conflict_branch)
                
                self.conflict_branches.append({
                    'number': pr.number,
                    'title': pr.title,
                    'branch': pr.head.ref,
                    'conflict_branch': conflict_branch,
                    'conflicts': conflicts
                })
            
            # Clean up working directory
            target_branch = self.identify_target_branch(pr)
            self.run_git_command(['git', 'checkout', target_branch], check=False)
            self.run_git_command(['git', 'reset', '--hard', f'origin/{target_branch}'], check=False)
    
    def print_summary(self):
        """Print a summary of all operations."""
        print("\n" + "="*80)
        print("PR MANAGEMENT SUMMARY")
        print("="*80)
        
        print(f"\n✓ Successfully Merged and Deleted ({len(self.successfully_merged)}):")
        if self.successfully_merged:
            for pr in self.successfully_merged:
                print(f"  - PR #{pr['number']}: {pr['title']}")
                print(f"    Branch: {pr['branch']}")
        else:
            print("  (none)")
        
        print(f"\n⚠️  Moved to Conflict Branch ({len(self.conflict_branches)}):")
        if self.conflict_branches:
            for pr in self.conflict_branches:
                print(f"  - PR #{pr['number']}: {pr['title']}")
                print(f"    Original: {pr['branch']}")
                print(f"    Conflicts: {pr['conflict_branch']}")
                print(f"    Files: {', '.join(pr['conflicts'])}")
        else:
            print("  (none)")
        
        print("\n" + "="*80)
    
    def run(self):
        """Main execution method."""
        print("Starting PR Manager...")
        print(f"Repository: {self.repo.full_name}\n")
        
        # Fetch all branches
        self.fetch_branches()
        
        # Get open PRs
        prs = self.get_open_prs()
        print(f"\nFound {len(prs)} open PR(s)")
        
        if not prs:
            print("No open PRs to process.")
            return
        
        # Process each PR
        for pr in prs:
            try:
                self.process_pr(pr)
            except Exception as e:
                print(f"\n✗ Error processing PR #{pr.number}: {e}")
                import traceback
                traceback.print_exc()
                # Continue with next PR
                continue
        
        # Print summary
        self.print_summary()


def main():
    """Main entry point."""
    # Get environment variables
    token = os.environ.get('GITHUB_TOKEN')
    repository = os.environ.get('REPOSITORY')
    
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    if not repository:
        print("Error: REPOSITORY environment variable not set")
        sys.exit(1)
    
    # Create and run manager
    manager = PRManager(token, repository)
    manager.run()


if __name__ == '__main__':
    main()
