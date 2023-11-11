import unittest
from unittest.mock import MagicMock, patch
from your_module import GitHubRepoCreator

class TestGitHubRepoCreator(unittest.TestCase):

    @patch('github.Github')
    def setUp(self, mock_github):
        self.mock_github = mock_github
        self.repo_creator = GitHubRepoCreator(
            repo_name='test_repo',
            org='test_org',
            access_token='test_token',
            url='https://github.com/api/v3'
        )

    @patch('github.Organization')
    def test_create_repository_success(self, mock_org):
        mock_repo = MagicMock()
        mock_org.create_repo.return_value = mock_repo
        self.repo_creator._github_repo = None  # Simulate uninitialized repo
        self.repo_creator.create_repository(private=False)
        mock_org.assert_called_once_with(self.repo_creator.g, 'test_org')
        mock_org.create_repo.assert_called_once_with(
            self.repo_creator.repo_name, private=False, auto_init=True
        )
        mock_repo.rename_branch.assert_called_once_with('master', 'develop')

    def test_create_repository_repo_exists(self):
        # Simulate the case where the repository already exists
        mock_repo = MagicMock()
        self.repo_creator._github_repo = mock_repo
        self.repo_creator.create_repository(private=False)
        mock_repo.get_repo.assert_called_once_with(self.repo_creator.repo_name)

    def test_create_repository_error(self):
        # Simulate an error during repository creation
        self.repo_creator._github_repo = None
        with patch.object(self.repo_creator.github_org, 'create_repo', side_effect=Exception('Test Error')):
            with self.assertRaises(Exception):
                self.repo_creator.create_repository(private=False)

    @patch('github.Repository')
    def test_create_feature_branch_success(self, mock_repo):
        # Simulate a successful creation of a feature branch
        mock_branch = MagicMock()
        mock_repo.get_branch.return_value = mock_branch
        self.repo_creator._github_repo = mock_repo
        result = self.repo_creator.create_feature_branch('feature_branch')
        self.assertTrue(result)
        mock_repo.get_branch.assert_called_once_with('develop')
        mock_repo.create_git_ref.assert_called_once_with(ref='refs/heads/feature_branch', sha=mock_branch.commit.sha)

    def test_create_feature_branch_repo_not_initialized(self):
        # Simulate creating a feature branch without initializing the GitHub repo
        self.repo_creator._github_repo = None
        with patch('builtins.print') as mock_print:
            result = self.repo_creator.create_feature_branch('feature_branch')
            self.assertFalse(result)
            mock_print.assert_called_once_with("GitHub repo is not initialized ")

    # Additional tests for create_feature_branch to cover error scenarios

    @patch('github.Repository')
    def test_create_release_branch_success(self, mock_repo):
        # Simulate a successful creation of a release branch
        mock_branch = MagicMock()
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.get_branches.return_value = []
        self.repo_creator._github_repo = mock_repo
        result = self.repo_creator.create_release_branch('v1.0.0')
        self.assertTrue(result)
        mock_repo.get_branch.assert_called_once_with('develop')
        mock_repo.create_git_ref.assert_called_once_with(ref='refs/heads/release/v1.0.0', sha=mock_branch.commit.sha)

    def test_create_release_branch_already_exists(self):
        # Simulate creating a release branch that already exists
        mock_branch = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.get_branches.return_value = [mock_branch]
        self.repo_creator._github_repo = mock_repo
        with patch('builtins.print') as mock_print:
            result = self.repo_creator.create_release_branch('v1.0.0')
            self.assertTrue(result)
            mock_print.assert_called_once_with('release branch already exists')

    # Additional tests for create_release_branch to cover error scenarios

    # Test cases for add_branch_protection and verify_status_checks can be similarly added

if __name__ == '__main__':
    unittest.main()


import pytest
from your_module import GitHubRepoCreator

@pytest.fixture
def github_repo_creator():
    return GitHubRepoCreator(
        repo_name='test_repo',
        org='test_org',
        access_token='test_token',
        url='https://github.com/api/v3'
    )

def test_create_repository(github_repo_creator):
    github_repo_creator.create_repository(private=False)
    assert github_repo_creator._github_repo is not None

def test_create_feature_branch(github_repo_creator):
    github_repo_creator.create_repository(private=False)
    result = github_repo_creator.create_feature_branch('feature_branch')
    assert result is True
    # Add assertions based on the expected behavior

def test_create_release_branch(github_repo_creator):
    github_repo_creator.create_repository(private=False)
    result = github_repo_creator.create_release_branch('v1.0.0')
    assert result is True
    # Add assertions based on the expected behavior

def test_add_branch_protection(github_repo_creator):
    github_repo_creator.create_repository(private=False)
    github_repo_creator.add_branch_protection()
    # Add assertions based on the expected behavior

def test_verify_status_checks(github_repo_creator):
    github_repo_creator.create_repository(private=False)
    github_repo_creator.verify_status_checks()
    # Add assertions based on the expected behavior

# Add more functional tests as needed

if __name__ == '__main__':
    pytest.main(['-v', 'test_github_repo_creator_functional.py'])

