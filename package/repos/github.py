from django.conf import settings

try:
    from github2.client import Github
except ImportError:
    # skipping this so we can generate docs
    pass

from base_handler import BaseHandler
from core.restconsumer import RestConsumer
from package.utils import uniquer

class OldGitHubHandler(BaseHandler):
    title = "Github"
    url_regex = '(http|https|git)://github.com/'
    url = 'https://github.com'
    repo_regex = r'(?:http|https|git)://github.com/[^/]*/([^/]*)/{0,1}'
    slug_regex = repo_regex

    def _github_client(self):
        if hasattr(settings, "GITHUB_ACCOUNT") and hasattr(settings, "GITHUB_KEY"):
            github   = RestConsumer(base_url='https://api.github.com', username=settings.GITHUB_ACCOUNT, api_token=settings.GITHUB_KEY)
        else:
            github   = RestConsumer(base_url='https://api.github.com')
        return github

    def fetch_metadata(self, package):
        github = self._github_client()

        username, repo_name = package.repo_name().split('/')
        repo = github.repos[username][repo_name]()
        package.repo_watchers    = repo['watchers']
        package.repo_forks       = repo['forks']
        package.repo_description = repo['description']

        #/repos/:user/:repo/collaborators
        collaborators = [x['login'] for x in github.repos[username][repo_name].collaborators()]
        collaborators += [x['login'] for x in github.repos[username][repo_name].contributors()]
        if collaborators:
            package.participants = ','.join(uniquer(collaborators))

        return package

    def fetch_commits(self, package):
        from package.models import Commit # Import placed here to avoid circular dependencies
        github = self._github_client()
        username, repo_name = package.repo_name().split('/')        
        # /repos/:user/:repo/commits
        for commit in github.github.repos[username][repo_name].commits():
            commit, created = Commit.objects.get_or_create(package=package, commit_date=commit.committed_date)


class GitHubHandler(BaseHandler):
    title = "Github"
    url_regex = '(http|https|git)://github.com/'
    url = 'https://github.com'
    repo_regex = r'(?:http|https|git)://github.com/[^/]*/([^/]*)/{0,1}'
    slug_regex = repo_regex

    def _github_client(self):
        if hasattr(settings, "GITHUB_ACCOUNT") and hasattr(settings, "GITHUB_KEY"):
            github   = Github(username=settings.GITHUB_ACCOUNT, api_token=settings.GITHUB_KEY)
        else:
            github   = Github()
        return github

    def fetch_metadata(self, package):
        github = self._github_client()

        repo_name = package.repo_name()
        repo = github.repos.show(repo_name)
        package.repo_watchers    = repo.watchers
        package.repo_forks       = repo.forks
        package.repo_description = repo.description

        collaborators = github.repos.list_collaborators(repo_name) + [x['login'] for x in github.repos.list_contributors(repo_name)]
        if collaborators:
            package.participants = ','.join(uniquer(collaborators))

        return package

    def fetch_commits(self, package):
        from package.models import Commit # Import placed here to avoid circular dependencies
        github = self._github_client()
        for commit in github.commits.list(package.repo_name(), "master"):
            commit, created = Commit.objects.get_or_create(package=package, commit_date=commit.committed_date)

repo_handler = GitHubHandler()
