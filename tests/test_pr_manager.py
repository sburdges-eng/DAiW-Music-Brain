#!/usr/bin/env python3
"""
Unit tests for PR Manager script.

This tests the core logic without requiring GitHub credentials.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add script directory to path
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.github', 'scripts')
sys.path.insert(0, script_dir)

from pr_manager import PRManager


class TestPRManager(unittest.TestCase):
    """Test cases for PRManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock GitHub client
        with patch('pr_manager.Github'):
            self.manager = PRManager('fake_token', 'owner/repo')
            self.manager.repo = Mock()
    
    def test_initialization(self):
        """Test PRManager initialization."""
        self.assertEqual(self.manager.successfully_merged, [])
        self.assertEqual(self.manager.conflict_branches, [])
    
    def test_identify_target_branch(self):
        """Test target branch identification."""
        pr = Mock()
        pr.base.ref = 'main'
        
        target = self.manager.identify_target_branch(pr)
        self.assertEqual(target, 'main')
    
    def test_get_conflicting_files_parsing(self):
        """Test parsing of conflicting files from git output."""
        # Mock git command output
        with patch.object(self.manager, 'run_git_command') as mock_git:
            mock_git.return_value = (0, "file1.py\nfile2.py\nfile3.md\n", "")
            
            conflicts = self.manager.get_conflicting_files()
            
            self.assertEqual(len(conflicts), 3)
            self.assertIn('file1.py', conflicts)
            self.assertIn('file2.py', conflicts)
            self.assertIn('file3.md', conflicts)
    
    def test_successfully_merged_tracking(self):
        """Test that successfully merged PRs are tracked."""
        pr_info = {
            'number': 1,
            'title': 'Test PR',
            'branch': 'feature/test'
        }
        
        self.manager.successfully_merged.append(pr_info)
        
        self.assertEqual(len(self.manager.successfully_merged), 1)
        self.assertEqual(self.manager.successfully_merged[0]['number'], 1)
    
    def test_conflict_branches_tracking(self):
        """Test that conflict branches are tracked."""
        conflict_info = {
            'number': 2,
            'title': 'Conflict PR',
            'branch': 'feature/conflict',
            'conflict_branch': 'conflicts/feature/conflict',
            'conflicts': ['file1.py', 'file2.py']
        }
        
        self.manager.conflict_branches.append(conflict_info)
        
        self.assertEqual(len(self.manager.conflict_branches), 1)
        self.assertEqual(self.manager.conflict_branches[0]['number'], 2)
        self.assertEqual(len(self.manager.conflict_branches[0]['conflicts']), 2)
    
    def test_run_git_command_success(self):
        """Test git command execution with success."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='success', stderr='')
            
            returncode, stdout, stderr = self.manager.run_git_command(['git', 'status'], check=False)
            
            self.assertEqual(returncode, 0)
            self.assertEqual(stdout, 'success')
    
    def test_run_git_command_failure(self):
        """Test git command execution with failure."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=1, stdout='', stderr='error')
            
            returncode, stdout, stderr = self.manager.run_git_command(['git', 'invalid'], check=False)
            
            self.assertEqual(returncode, 1)
            self.assertEqual(stderr, 'error')


class TestPRManagerIntegration(unittest.TestCase):
    """Integration tests for PR Manager (without actual GitHub API calls)."""
    
    @patch('pr_manager.Github')
    def test_get_open_prs(self, mock_github):
        """Test retrieving open PRs."""
        # Setup mock
        mock_repo = Mock()
        mock_pr1 = Mock(number=1, title='PR 1', state='open')
        mock_pr2 = Mock(number=2, title='PR 2', state='open')
        mock_repo.get_pulls.return_value = [mock_pr1, mock_pr2]
        
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance
        
        # Create manager
        manager = PRManager('fake_token', 'owner/repo')
        prs = manager.get_open_prs()
        
        # Verify
        self.assertEqual(len(prs), 2)
        self.assertEqual(prs[0].number, 1)
        self.assertEqual(prs[1].number, 2)
    
    @patch('pr_manager.Github')
    def test_comment_on_pr(self, mock_github):
        """Test commenting on a PR."""
        # Setup
        mock_pr = Mock(number=1)
        
        manager = PRManager('fake_token', 'owner/repo')
        conflicts = ['file1.py', 'file2.md']
        
        # Execute
        manager.comment_on_pr(mock_pr, conflicts, 'conflicts/feature-branch')
        
        # Verify comment was created
        mock_pr.create_issue_comment.assert_called_once()
        call_args = mock_pr.create_issue_comment.call_args[0][0]
        self.assertIn('file1.py', call_args)
        self.assertIn('file2.md', call_args)
        self.assertIn('conflicts/feature-branch', call_args)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPRManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPRManagerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
