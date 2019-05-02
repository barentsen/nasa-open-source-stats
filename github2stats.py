"""Retrieve statistics on a GitHub repository."""
import os
import requests

TOKEN = open(os.path.expanduser("~/.github/token")).read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def query_github(query):
    """Query the GitHub API."""
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query},
                            headers=HEADERS)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}"
                        "".format(request.status_code, query))


def github2stats(repository_owner="keplergo", repository_name="lightkurve"):
    """Retrieves GitHub stats given a GitHub username and repository."""
    query = """
        query RepoStats {
            repository(owner:"%s", name:"%s") {
                createdAt
            pushedAt
            shortDescriptionHTML
            parent {
                id
            }
            primaryLanguage {
                name
            }
            licenseInfo {
                        name
                spdxId
                pseudoLicense
            }
            forks(first:1) {
                totalCount
                edges() { node() { id } }
            }
            stargazers(first:1) {
                totalCount
                edges() { node() { id } }
            }
            issues(first:1) {
                totalCount
                edges() { node() { id } }
            }
            closedIssues: issues(first:1, states: [CLOSED]) {
                totalCount
                edges() { node() { id } }
            }
            collaborators(first:1) {
                totalCount
                edges() { node() { id } }
            }
            }

        rateLimit {
            cost
            remaining
        }
    }
    """ % (repository_owner, repository_name)
    result = query_github(query)
    return result


def get_rate_limit():
    query = """
    {
    viewer {
        login
    }
    rateLimit {
        limit
        cost
        remaining
        resetAt
    }
    }
    """
    return query_github(query)


if __name__ == "__main__": 
    print(github2stats())     
    print(get_rate_limit())
