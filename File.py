from github import Github
import git
import os
import re

class GitHubRepoCreator:
    def __init(self, access_token):
        self.g = Github(access_token)

    def create_repository(self, org_name, repo_name, private=False):
        org = self.g.get_organization(org_name)
        repo = org.create_repo(repo_name, private=private)
        return repo

    def create_branches(self, repo, branch_names):
        master_sha = repo.get_branch('master').commit.sha
        for branch_name in branch_names:
            repo.create_git_ref(ref=f'refs/heads/{branch_name}', sha=master_sha)

    def rename_master_to_develop(self, repo_path):
        try:
            repo = git.Repo(repo_path)
            # Make sure we are on the 'master' branch
            repo.git.checkout('master')
            # Rename the branch to 'develop'
            repo.git.branch('-m', 'develop')
            # Push the new 'develop' branch
            repo.git.push('origin', 'develop', set_upstream=True)
            return True
        except Exception as e:
            print(f"Error renaming branch: {e}")
            return False

    def create_feature_branch(self, repo_path, branch_name):
        try:
            repo = git.Repo(repo_path)
            # Make sure we are on the 'develop' branch
            repo.git.checkout('develop')
            # Create a new feature branch
            repo.git.checkout(b=branch_name)
            # Push the new feature branch
            repo.git.push('origin', branch_name, set_upstream=True)
            return True
        except Exception as e:
            print(f"Error creating feature branch: {e}")
            return False

    def create_release_branch(self, repo_path, branch_pattern):
        try:
            repo = git.Repo(repo_path)
            # Make sure we are on the 'develop' branch
            repo.git.checkout('develop')

            # Find the latest release branch matching the pattern
            release_branches = [b for b in repo.branches if re.match(branch_pattern, b.name)]
            if release_branches:
                # Determine the next release branch number
                latest_branch = max(release_branches, key=lambda b: int(b.name.split("/")[-1]))
                next_number = int(latest_branch.name.split("/")[-1]) + 1
            else:
                # If no existing release branches, start from 0
                next_number = 0

            new_branch_name = f'release/{next_number}.0.0'

            # Create the new release branch
            repo.git.checkout(b=new_branch_name)
            # Push the new release branch
            repo.git.push('origin', new_branch_name, set_upstream=True)
            return True
        except Exception as e:
            print(f"Error creating release branch: {e}")
            return False

# Example usage:
# github_creator = GitHubRepoCreator('YOUR_ACCESS_TOKEN')
# repo = github_creator.create_repository('your-org', 'repo-name', private=False)
# github_creator.create_branches(repo, ['develop', 'feature'])
# github_creator.rename_master_to_develop('/path/to/your/repo')
# github_creator.create_feature_branch('/path/to/your/repo', 'my-feature-branch')
# github_creator.create_release_branch('/path/to/your/repo', r'release/\d+\.\d+\.\d+')
