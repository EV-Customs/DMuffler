#!/usr/bin/env python3
"""
Dependabot PR Auto-Approver

This script automatically approves and merges Dependabot pull requests
that pass all required checks. It's designed to be run as a GitHub Action.
"""

import os
import re
from typing import List

from github import Github, GithubException

# Initialize GitHub client
github = Github(os.getenv("GITHUB_TOKEN"))
repo = github.get_repo(os.getenv("GITHUB_REPOSITORY"))


def get_dependabot_prs():
    """Get all open Dependabot PRs in the repository."""
    return [pr for pr in repo.get_pulls(state="open") if pr.user.login == "dependabot[bot]"]


def pr_has_passing_checks(pr) -> bool:
    """Check if all required checks have passed for a PR."""
    # Get the commit status
    commit = repo.get_commit(pr.head.sha)
    status = commit.get_combined_status()

    # Check if all statuses are success
    if status.state != "success":
        return False

    # Check required checks if any
    required_checks = get_required_checks()
    if required_checks:
        check_runs = commit.get_check_runs()
        for check in required_checks:
            if not any(run.name == check and run.conclusion == "success" for run in check_runs):
                return False

    return True


def get_required_checks() -> List[str]:
    """Get the list of required checks that must pass before merging."""
    # This can be customized based on your repository's requirements
    return ["test", "lint"]


def approve_pr(pr) -> bool:
    """Approve a pull request if not already approved."""
    # Check if already approved by this bot
    for review in pr.get_reviews():
        if review.user.login == "github-actions[bot]" and review.state == "APPROVED":
            return True

    # Approve the PR
    try:
        pr.create_review(event="APPROVE")
        return True
    except GithubException as e:
        print(f"Error approving PR: {e}")
        return False


def add_comment(pr, comment: str) -> None:
    """Add a comment to a pull request."""
    try:
        pr.create_issue_comment(comment)
    except Exception as e:
        print(f"Error adding comment: {e}")
        # Don't raise the exception, just log it


def merge_pr(pr) -> bool:
    """Merge a pull request if it's mergeable."""
    try:
        if not pr.mergeable:
            return False

        # Format commit message
        title = pr.title
        if match := re.match(r"^Bump (.+?) from ([\d.]+) to ([\d.]+)", title):
            pkg, old_ver, new_ver = match.groups()
            title = f"chore(deps): Bump {pkg} from {old_ver} to {new_ver}"

        pr.merge(commit_title=title, merge_method="squash")
        return True
    except Exception as e:
        print(f"Error merging PR: {e}")
        return False


def main() -> None:
    """Main function to process Dependabot PRs."""
    print("Checking for Dependabot PRs...")

    for pr in get_dependabot_prs():
        print(f"Processing PR #{pr.number}: {pr.title}")

        if not pr_has_passing_checks(pr):
            print(f"PR #{pr.number} does not have passing checks, skipping")
            continue

        print(f"Approving PR #{pr.number}")
        if not approve_pr(pr):
            print(f"Failed to approve PR #{pr.number}")
            continue

        print(f"Merging PR #{pr.number}")
        if not merge_pr(pr):
            print(f"Failed to merge PR #{pr.number}")
        else:
            print(f"Successfully merged PR #{pr.number}")


if __name__ == "__main__":
    main()
