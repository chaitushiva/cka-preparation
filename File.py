import unittest
from unittest.mock import patch, Mock
from argparse import Namespace
from gitoperations.newrepo.newrepo import GitHubRepoCreator, GitHubException
from your_script import validatedFeatureBranch, validatedReleaseBranch, main

class TestGitHubRepoCreator(unittest.TestCase):
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_repository')
    def test_create_repository_success(self, mock_create_repo):
        # Mock successful create_repository call
        mock_create_repo.return_value = Mock()
        args = Namespace(repo_name='test_repo', org='test_org')
        github_creator = GitHubRepoCreator(org=args.org, repo_name=args.repo_name, access_token='dummy_token')
        repo = github_creator.create_repository()
        self.assertIsNotNone(repo)
        mock_create_repo.assert_called_once()

    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_repository')
    def test_create_repository_exception(self, mock_create_repo):
        # Mock create_repository call raising GitHubException
        mock_create_repo.side_effect = GitHubException('Failed to create repository')
        args = Namespace(repo_name='test_repo', org='test_org')
        github_creator = GitHubRepoCreator(org=args.org, repo_name=args.repo_name, access_token='dummy_token')
        with self.assertRaises(GitHubException):
            github_creator.create_repository()
        mock_create_repo.assert_called_once()

class TestMainFunction(unittest.TestCase):
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_repository')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_feature_branch')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_release_branch')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.add_branch_protection')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.verify_status_checks')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.__init__', return_value=None)
    @patch('gitoperations.newrepo.newrepo.os.environ.get', side_effect=['dummy_token'])
    @patch('gitoperations.newrepo.newrepo.logger')
    @patch('gitoperations.newrepo.newrepo.sys.exit')
    def test_main_function(self, mock_sys_exit, mock_logger, mock_os_getenv, mock_init, mock_verify_status_checks,
                          mock_add_branch_protection, mock_create_release_branch, mock_create_feature_branch,
                          mock_create_repo):
        # Mocking main function with successful execution
        args = Namespace(repo_name='test_repo', org='test_org', feature_branch='feature-branch', release_branch_tag='1.0.0')
        main()
        mock_init.assert_called_once_with(org='test_org', repo_name='test_repo', access_token='dummy_token')
        mock_create_repo.assert_called_once()
        mock_create_feature_branch.assert_called_once_with(branch='feature-branch')
        mock_create_release_branch.assert_called_once_with(branch='1.0.0')
        mock_add_branch_protection.assert_called_once()
        mock_verify_status_checks.assert_called_once()
        mock_logger.info.assert_called_with(" we are here")
        mock_sys_exit.assert_not_called()

    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_repository')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_feature_branch')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.create_release_branch')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.add_branch_protection')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.verify_status_checks')
    @patch('gitoperations.newrepo.newrepo.GitHubRepoCreator.__init__', return_value=None)
    @patch('gitoperations.newrepo.newrepo.os.environ.get', side_effect=['dummy_token'])
    @patch('gitoperations.newrepo.newrepo.logger')
    @patch('gitoperations.newrepo.newrepo.sys.exit')
    def test_main_function_exception(self, mock_sys_exit, mock_logger, mock_os_getenv, mock_init,
                                     mock_verify_status_checks, mock_add_branch_protection,
                                     mock_create_release_branch, mock_create_feature_branch, mock_create_repo):
        # Mocking main function with an exception during execution
        mock_create_repo.side_effect = GitHubException('Failed to create repository')
        args = Namespace(repo_name='test_repo', org='test_org', feature_branch='feature-branch', release_branch_tag='1.0.0')
        main()
        mock_logger.error.assert_called_once()
        mock_sys_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
