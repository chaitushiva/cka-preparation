import git
import os
import re
import sys

# Get the PAT and username from environment variables
pat = os.environ.get('GIT_PAT')
username = os.environ.get('GIT_USERNAME')

if not pat or not username:
    print("Please set GIT_PAT and GIT_USERNAME environment variables.")
    exit(1)

# Validate the input using regular expression
def validate_version(version):
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print("Invalid version format. Please use major.minor.patch format.")
        exit(1)

# Create release branch function
def create_release_branch(version):
    repo = git.Repo('/path/to/your/repo')

    # Split the version input into major, minor, and patch components
    major_version, minor_version, patch_version = map(int, version.split('.'))

    # Create the release branch name
    release_branch_name = f'release/{major_version}.{minor_version}.{patch_version}'

    # Create a new branch from 'main' or any other base branch
    repo.git.checkout('main')
    new_branch = repo.create_head(release_branch_name)
    new_branch.checkout()
    print(f"Created release branch: {release_branch_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_release_branch.py <version>")
        exit(1)

    version_input = sys.argv[1]
    validate_version(version_input)
    create_release_branch(version_input)
