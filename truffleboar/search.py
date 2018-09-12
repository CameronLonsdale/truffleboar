"""Analysis module"""

import git
import github
import datetime
import tempfile
import hashlib

from truffleboar.structures import Feature, Artifact
from truffleboar.util import clone_git_repo

from typing import Optional, Iterable, Callable


GH_HANDLE = None


def search_diff(diff, analysers: Iterable[Callable]) -> Iterable[Artifact]:
    """
    Search a commit diff for features
    This function returns artifacts
    """
    artifacts = []
    for blob in diff:
        raw_text = blob.diff.decode('utf-8', errors='replace')
        if raw_text.startswith("Binary files"):
            continue

        for analysis_artifacts in [analyse(raw_text) for analyse in analysers]:
            artifacts += analysis_artifacts

    return artifacts


def search_branch(repo, branch_name: str, analysers: Iterable[Callable], max_depth: int=100000) -> Iterable[Feature]:
    """
    Search a branch for features
    """
    prev_commit = None
    results = []

    # Iterate commits from newest to oldest
    for curr_commit in repo.iter_commits(branch_name, max_count=max_depth):

        # If the prev_commit is None then curr_commit is the newest commit and there is nothing to diff
        # it with. We continue to get the next commit
        if prev_commit is None:
            prev_commit = curr_commit
            continue

        # TODO: Add optimisation to avoid rescanning already scanned diff
   
        diff = prev_commit.diff(curr_commit, create_patch=True)
        issues = search_diff(diff, analysers)
        if issues:
            results.append(Feature(
                date=datetime.datetime.fromtimestamp(prev_commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
                source='Commit',
                section='Blob',
                identifier=prev_commit.hexsha,
                location=branch_name,
                artifacts=issues
            ))

        prev_commit = curr_commit

    # Handling the first commit
    diff = curr_commit.diff(git.NULL_TREE, create_patch=True)
    issues = search_diff(diff, analysers)
    if issues:
        results.append(Feature(
            date=datetime.datetime.fromtimestamp(prev_commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
            source='Commit',
            section='Blob',
            identifier=prev_commit.hexsha,
            location=branch_name,
            artifacts=issues
        ))

    return results


def search_commits(project_full_name: str, analysers: Iterable[Callable], branch: Optional[str]):
    """
    Search every commit diff for features
    """
    git_url = f"https://github.com/{project_full_name}"
    project_path = clone_git_repo(git_url)
    repo = git.Repo(project_path)

    results = []

    # TODO: check the logic of fetch() if branch is none maybe we could not
    if branch:
        branches = repo.remotes.origin.fetch(branch)
    else:
        branches = repo.remotes.origin.fetch()

    for branch in branches:
        results += search_branch(repo, branch.name, analysers)

    return results

def search_pull_request(pull_request: github.PullRequest.PullRequest, analysers: Iterable[Callable]):
    """Find features inside a pull request"""
    features = []

    # Check the title
    title_artifacts = [analyse(pull_request.title) for analyse in analysers]
    for artifacts in title_artifacts:
        if artifacts:
            features.append(Feature(
                date=pull_request.created_at,
                source='Pull Request',
                section='Title',
                identifier=pull_request.id,
                location=pull_request.url,
                artifacts=artifacts
            ))

    # Check the body
    body_artifacts = [analyse(pull_request.title) for analyse in analysers]
    for artifacts in body_artifacts:
        if artifacts:
            features.append(Feature(
                date=pull_request.created_at,
                source='Pull Request',
                section='Description',
                identifier=pull_request.id,
                location=pull_request.url,
                artifacts=artifacts
            ))

    # Check each comment
    for comment in pull_request.get_comments():
        comment_artifacts = truffleboar.checks.regex_check(comment.body, regex_rules)

        for artifacts in comment_artifacts:
            if artifacts:
                features.append(Feature(
                    date=comment.created_at,
                    source='Pull Request',
                    section='Comment',
                    identifier=comment.id,
                    location=comment.url,
                    artifacts=artifacts
                ))


    # TODO: Check each commit for features (We need to check the code first and make sure we don't double up on our checks)

    return features


def search_pull_requests(project_name: str, analysers: Iterable[Callable]) -> Iterable[Feature]:
    """Find features inside of Pull Requests"""
    repo = GH_HANDLE.get_repo(project_name)
    pull_requests = [*repo.get_pulls(state='open'), *repo.get_pulls(state='closed')]

    features = []
    for pr in pull_requests: 
        pr_features = search_pull_request(pr, analysers)
        if pr_features:
            features += pr_features

        return features


def search_issue(issue: github.Issue.Issue, analysers: Iterable[Callable]) -> Iterable[Feature]:
    """Find features inside of an issue"""

    features = []

    # Check the title
    title_artifacts = [analyse(issue.title) for analyse in analysers]
    for artifacts in title_artifacts:
        if artifacts:
            features.append(Feature(
                date=issue.created_at,
                source='Issue',
                section='Title',
                identifier=issue.id,
                location=issue.html_url,
                artifacts=artifacts
            ))


    # Check the body
    body_artifacts = [analyse(issue.body) for analyse in analysers]
    for artifacts in body_artifacts:
        if artifacts:
            features.append(Feature(
                date=issue.created_at,
                source='Issue',
                section='Description',
                identifier=issue.id,
                location=issue.html_url,
                artifacts=artifacts
            ))

    # Check each comment
    for comment in issue.get_comments():
        comment_artifacts = [analyse(comment.body) for analyse in analysers]

        for artifacts in comment_artifacts:
            if artifacts:
                features.append(Feature(
                    date=comment.created_at,
                    source='Issue',
                    section='Comment',
                    identifier=comment.id,
                    location=comment.html_url,
                    artifacts=artifacts
                ))

    return features


def search_issues(project_full_name: str, analysers: Iterable[Callable]) -> Iterable[Feature]:
    """Search every issue in a project for features"""
    repo = GH_HANDLE.get_repo(project_full_name)
    issues = [*repo.get_issues(state='open'), *repo.get_issues(state='closed')]

    features = []
    for issue in issues: 
        issue_features = search_issue(issue, analysers)
        if issue_features:
            features += issue_features

    return features


def find_features(project_full_name: str, analysers: Iterable[Callable], branch:Optional[str] = None, auth_token: Optional[str] = None):
    """Find features in a GitHub project"""
    global GH_HANDLE
    GH_HANDLE = github.Github(auth_token)

    features = []

    # TODO: These should be customisable
    features = search_commits(project_full_name, analysers, branch)
    features += search_issues(project_full_name, analysers)
    features += search_pull_requests(project_full_name, analysers)

    return features
