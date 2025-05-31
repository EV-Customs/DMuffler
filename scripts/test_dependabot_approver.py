#!/usr/bin/env python3
"""
Test script for the Dependabot auto-approver functionality.

This module contains tests for the Dependabot PR approval and merging logic.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment variables for testing
os.environ["GITHUB_REPOSITORY"] = "test-owner/test-repo"
os.environ["GITHUB_TOKEN"] = "test-token"

# Import the module after setting up the environment
with patch("github.Github"):
    from scripts.approve_dependabot_prs import (
        get_dependabot_prs,
        pr_has_passing_checks,
        approve_pr,
        add_comment,
        merge_pr,
        get_required_checks,
        main,
    )


@pytest.fixture(autouse=True)
def setup_mocks():
    """Set up all necessary mocks for testing."""
    with patch("github.Github") as mock_github, patch(
        "scripts.approve_dependabot_prs.github"
    ) as mock_module_github, patch("scripts.approve_dependabot_prs.repo") as mock_module_repo:

        # Set up mock GitHub instance
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_module_github.get_repo.return_value = mock_repo
        mock_module_repo = mock_repo

        yield {
            "github": mock_github,
            "repo": mock_repo,
            "module_github": mock_module_github,
            "module_repo": mock_module_repo,
        }


class TestDependabotApprover:
    """Test cases for the Dependabot auto-approver functionality."""

    def test_get_dependabot_prs(self, setup_mocks):
        """Test finding Dependabot PRs."""
        # Setup
        mock_repo = setup_mocks["repo"]
        mock_pr = MagicMock()
        mock_pr.user.login = "dependabot[bot]"
        mock_pr.title = "Bump test-package from 1.0.0 to 1.0.1"
        mock_pr.number = 1

        # Mock the pull requests
        mock_pulls = MagicMock()
        mock_pulls.__iter__.return_value = [mock_pr]
        mock_repo.get_pulls.return_value = mock_pulls

        # Test
        with patch("scripts.approve_dependabot_prs.repo", mock_repo):
            prs = list(get_dependabot_prs())
            assert len(prs) == 1
            assert prs[0].number == 1
            mock_repo.get_pulls.assert_called_once_with(state="open")

    def test_pr_has_passing_checks(self, setup_mocks):
        """Test if PR has passing checks."""
        # Setup
        mock_repo = setup_mocks["repo"]
        mock_pr = MagicMock()
        mock_pr.head.sha = "test_sha"

        # Mock the commit and status
        mock_commit = MagicMock()
        mock_status = MagicMock()

        # Test with passing checks
        mock_status.state = "success"
        mock_commit.get_combined_status.return_value = mock_status
        mock_repo.get_commit.return_value = mock_commit

        # Mock the repository in the module
        with patch("scripts.approve_dependabot_prs.repo", mock_repo):
            with patch("scripts.approve_dependabot_prs.get_required_checks", return_value=[]):
                # Mock the PR's repository
                mock_pr.base.repo = mock_repo
                assert pr_has_passing_checks(mock_pr) is True

            # Test with failing status
            mock_status.state = "failure"
            with patch("scripts.approve_dependabot_prs.get_required_checks", return_value=[]):
                assert pr_has_passing_checks(mock_pr) is False

            # Test with required checks
            with patch(
                "scripts.approve_dependabot_prs.get_required_checks", return_value=["test-check"]
            ):
                mock_check_run = MagicMock()
                mock_check_run.name = "test-check"
                mock_check_run.conclusion = "success"
                mock_commit.get_check_runs.return_value = [mock_check_run]

                # Status is still failing
                assert pr_has_passing_checks(mock_pr) is False

                # Now with passing status
                mock_status.state = "success"
                assert pr_has_passing_checks(mock_pr) is True

                # Failing check run
                mock_check_run.conclusion = "failure"
                assert pr_has_passing_checks(mock_pr) is False

    def test_approve_pr(self):
        """Test approving a PR."""
        # Setup
        mock_pr = MagicMock()
        mock_pr.get_reviews.return_value = []

        # Test approving a PR that needs approval
        assert approve_pr(mock_pr) is True
        mock_pr.create_review.assert_called_once_with(event="APPROVE")

        # Test already approved PR
        mock_pr.reset_mock()
        mock_review = MagicMock()
        mock_review.user.login = "github-actions[bot]"
        mock_review.state = "APPROVED"
        mock_pr.get_reviews.return_value = [mock_review]

        assert approve_pr(mock_pr) is True
        mock_pr.create_review.assert_not_called()

        # Test with existing non-approval review
        mock_pr.reset_mock()
        mock_review.state = "COMMENTED"
        mock_pr.get_reviews.return_value = [mock_review]

        assert approve_pr(mock_pr) is True
        mock_pr.create_review.assert_called_once_with(event="APPROVE")

    def test_merge_pr(self, setup_mocks):
        """Test merging a PR."""
        # Setup
        mock_pr = MagicMock()
        mock_pr.mergeable = True
        mock_pr.title = "Bump test-package from 1.0.0 to 1.0.1"

        # Test successful merge
        assert merge_pr(mock_pr) is True
        mock_pr.merge.assert_called_once()

        # Check merge was called with the correct arguments
        call_args = mock_pr.merge.call_args[1]
        assert call_args["merge_method"] == "squash"
        assert call_args["commit_title"].startswith(
            "chore(deps): Bump test-package from 1.0.0 to 1.0.1"
        )

        # Test non-mergeable PR
        mock_pr.reset_mock()
        mock_pr.mergeable = False
        assert merge_pr(mock_pr) is False
        mock_pr.merge.assert_not_called()

        # Test merge failure
        mock_pr.reset_mock()
        mock_pr.mergeable = True
        mock_pr.merge.side_effect = Exception("Merge failed")
        assert merge_pr(mock_pr) is False

    def test_add_comment(self):
        """Test adding a comment to a PR."""
        mock_pr = MagicMock()
        test_comment = "Test comment"

        # Test successful comment
        add_comment(mock_pr, test_comment)
        mock_pr.create_issue_comment.assert_called_once_with(test_comment)

        # Test comment with exception
        mock_pr.reset_mock()
        mock_pr.create_issue_comment.side_effect = Exception("API rate limit exceeded")

        # Should not raise an exception
        add_comment(mock_pr, test_comment)

    def test_get_required_checks(self):
        """Test getting the list of required checks."""
        # Test the default required checks
        assert get_required_checks() == ["test", "lint"]

    def test_main(self, setup_mocks, capsys):
        """Test the main function."""
        # Setup mocks
        mock_repo = setup_mocks["repo"]

        # Create a mock PR
        mock_pr = MagicMock()
        mock_pr.user.login = "dependabot[bot]"
        mock_pr.number = 1
        mock_pr.title = "Bump test-package from 1.0.0 to 1.0.1"
        mock_pr.mergeable = True

        # Mock the pull requests
        mock_pulls = MagicMock()
        mock_pulls.__iter__.return_value = [mock_pr]
        mock_repo.get_pulls.return_value = mock_pulls

        # Mock the commit status
        mock_commit = MagicMock()
        mock_status = MagicMock()
        mock_status.state = "success"
        mock_commit.get_combined_status.return_value = mock_status
        mock_repo.get_commit.return_value = mock_commit

        # Mock the check runs
        mock_check_run = MagicMock()
        mock_check_run.name = "test"
        mock_check_run.conclusion = "success"
        mock_commit.get_check_runs.return_value = [mock_check_run]

        # Run the main function
        with patch("scripts.approve_dependabot_prs.repo", mock_repo), patch(
            "scripts.approve_dependabot_prs.get_required_checks", return_value=["test"]
        ):
            # Mock the PR's repository
            mock_pr.base.repo = mock_repo

            # Run the main function
            main()

            # Check the output
            captured = capsys.readouterr()
            assert "Checking for Dependabot PRs..." in captured.out
            assert "Processing PR #1: Bump test-package from 1.0.0 to 1.0.1" in captured.out
            assert "Approving PR #1" in captured.out
            assert "Merging PR #1" in captured.out
            assert "Successfully merged PR #1" in captured.out

            # Verify the PR was approved and merged
            mock_pr.create_review.assert_called_once_with(event="APPROVE")
            mock_pr.merge.assert_called_once_with(
                commit_title="chore(deps): Bump test-package from 1.0.0 to 1.0.1",
                merge_method="squash",
            )

    def test_main_with_failing_checks(self, setup_mocks, capsys):
        """Test the main function with failing checks."""
        # Setup mocks
        mock_repo = setup_mocks["repo"]

        # Create a mock PR
        mock_pr = MagicMock()
        mock_pr.user.login = "dependabot[bot]"
        mock_pr.number = 1
        mock_pr.title = "Bump test-package from 1.0.0 to 1.0.1"

        # Mock the pull requests
        mock_pulls = MagicMock()
        mock_pulls.__iter__.return_value = [mock_pr]
        mock_repo.get_pulls.return_value = mock_pulls

        # Mock the commit status to be failing
        mock_commit = MagicMock()
        mock_status = MagicMock()
        mock_status.state = "failure"
        mock_commit.get_combined_status.return_value = mock_status
        mock_repo.get_commit.return_value = mock_commit

        # Run the main function
        with patch("scripts.approve_dependabot_prs.repo", mock_repo), patch(
            "scripts.approve_dependabot_prs.get_required_checks", return_value=["test"]
        ):
            # Mock the PR's repository
            mock_pr.base.repo = mock_repo

            # Run the main function
            main()

            # Check the output
            captured = capsys.readouterr()
            assert "PR #1 does not have passing checks, skipping" in captured.out

            # Verify the PR was not approved or merged
            mock_pr.create_review.assert_not_called()
            mock_pr.merge.assert_not_called()

    def test_main_with_merge_failure(self, setup_mocks, capsys):
        """Test the main function with a merge failure."""
        # Setup mocks
        mock_repo = setup_mocks["repo"]

        # Create a mock PR
        mock_pr = MagicMock()
        mock_pr.user.login = "dependabot[bot]"
        mock_pr.number = 1
        mock_pr.title = "Bump test-package from 1.0.0 to 1.0.1"
        mock_pr.mergeable = True  # PR is mergeable but will fail on merge

        # Mock the pull requests
        mock_pulls = MagicMock()
        mock_pulls.__iter__.return_value = [mock_pr]
        mock_repo.get_pulls.return_value = mock_pulls

        # Mock the commit status
        mock_commit = MagicMock()
        mock_status = MagicMock()
        mock_status.state = "success"
        mock_commit.get_combined_status.return_value = mock_status
        mock_repo.get_commit.return_value = mock_commit

        # Mock the check runs
        mock_check_run = MagicMock()
        mock_check_run.name = "test"
        mock_check_run.conclusion = "success"
        mock_commit.get_check_runs.return_value = [mock_check_run]

        # Mock the merge to raise an exception
        mock_pr.merge.side_effect = Exception("Merge conflict")

        # Run the main function
        with patch("scripts.approve_dependabot_prs.repo", mock_repo), patch(
            "scripts.approve_dependabot_prs.get_required_checks", return_value=["test"]
        ), patch("scripts.approve_dependabot_prs.pr_has_passing_checks", return_value=True):
            # Mock the PR's repository
            mock_pr.base.repo = mock_repo

            # Run the main function
            main()

            # Check the output
            captured = capsys.readouterr()
            assert "Failed to merge PR #1" in captured.out

            # Verify the PR was approved but merge failed
            mock_pr.create_review.assert_called_once_with(event="APPROVE")
            mock_pr.merge.assert_called_once()

    def test_approve_pr_error(self):
        """Test error handling in approve_pr function."""
        # Create a mock PR
        mock_pr = MagicMock()
        mock_pr.get_reviews.return_value = []

        # Create a mock exception
        from github import GithubException

        mock_exception = GithubException(
            status=403, data='{"message": "API rate limit exceeded"}', headers={}
        )
        mock_pr.create_review.side_effect = mock_exception

        # Test that the function handles the error and returns False
        assert approve_pr(mock_pr) is False
        mock_pr.create_review.assert_called_once_with(event="APPROVE")

    def test_merge_pr_error(self):
        """Test error handling in merge_pr function."""
        # Create a mock PR that's mergeable but will fail
        mock_pr = MagicMock()
        mock_pr.mergeable = True
        mock_pr.title = "Bump test-package from 1.0.0 to 1.0.1"
        mock_pr.merge.side_effect = Exception("Merge failed")

        # Test that the function handles the error and returns False
        assert merge_pr(mock_pr) is False
        mock_pr.merge.assert_called_once()

    def test_main_with_approval_failure(self, setup_mocks, capsys):
        """Test the main function when PR approval fails."""
        # Setup mocks
        mock_repo = setup_mocks["repo"]

        # Create a mock PR
        mock_pr = MagicMock()
        mock_pr.user.login = "dependabot[bot]"
        mock_pr.number = 1
        mock_pr.title = "Bump test-package from 1.0.0 to 1.0.1"

        # Mock the pull requests
        mock_pulls = MagicMock()
        mock_pulls.__iter__.return_value = [mock_pr]
        mock_repo.get_pulls.return_value = mock_pulls

        # Mock the commit status
        mock_commit = MagicMock()
        mock_status = MagicMock()
        mock_status.state = "success"
        mock_commit.get_combined_status.return_value = mock_status
        mock_repo.get_commit.return_value = mock_commit

        # Mock the check runs
        mock_check_run = MagicMock()
        mock_check_run.name = "test"
        mock_check_run.conclusion = "success"
        mock_commit.get_check_runs.return_value = [mock_check_run]

        # Mock the PR's repository
        mock_pr.base.repo = mock_repo

        # Run the main function with a failing approve_pr
        with patch("scripts.approve_dependabot_prs.repo", mock_repo), patch(
            "scripts.approve_dependabot_prs.get_required_checks", return_value=["test"]
        ), patch("scripts.approve_dependabot_prs.pr_has_passing_checks", return_value=True), patch(
            "scripts.approve_dependabot_prs.approve_pr", return_value=False
        ):
            main()

            # Check the output
            captured = capsys.readouterr()
            assert "Failed to approve PR #1" in captured.out

            # Verify the PR was not merged
            mock_pr.merge.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
