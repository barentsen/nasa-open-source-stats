"""Retrieve summary statistics on a GitHub repository.

Example use
-----------
>>> get_repo_stats("KeplerGO", "lightkurve")
{'repository_owner': 'KeplerGO',
 'repository_name': 'lightkurve',
 'pushedAt': '2019-05-02T17:04:34Z',
 'language': 'Python',
 'license': 'MIT',
 'pseudoLicense': False,
 'n_forks': 53,
 'n_stars': 95,
 'n_pullRequests': 263,
 'n_issues': 243,
 'n_issues_unique_authors': 46,
 'n_pullRequests_unique_authors': 29}

Requirements
------------
This module requires you obtain and store a personal GitHub API token
in "~/.github/token".
"""
import os
import requests
import json
import numpy as np
from tqdm import tqdm


TOKEN = open(os.path.expanduser("~/.github/token")).read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def query_github(query):
    """Query the GitHub API documented at https://developer.github.com/v4.
    
    Parameters
    ----------
    query : str
        GraphQL query.
    
    Returns
    -------
    result : dict
        Dictionary representing the API's JSON response.
    """
    request = requests.post('https://api.github.com/graphql',
                            json={'query': query},
                            headers=HEADERS)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}"
                        "".format(request.status_code, query))


def get_rate_limit():
    """Returns the status of GitHub API's rate limits."""
    query = """
    {
        rateLimit {
            limit
            cost
            remaining
            resetAt
        }
    }
    """
    return query_github(query)


def get_easy_stats(repository_owner="keplergo", repository_name="lightkurve"):
    """Retrieves GitHub stats given a GitHub username and repository.
    
    This function retrieves only the stats that can be obtained using a single
    GraphQL query.

    Returns
    -------
    stats : dict
        Dictionary containing summary stats.
    """
    query = """
        query RepoStats {
            repository(owner:"%s", name:"%s") {
                createdAt
                pushedAt
                shortDescriptionHTML
                primaryLanguage {
                    name
                }
                licenseInfo {
                    spdxId
                    pseudoLicense
                }
                forks(first:0) {
                    totalCount
                }
                stargazers(first:0) {
                    totalCount
                }
                pullRequests(first:0) {
                    totalCount
                }
                issues(first:0) {
                    totalCount
                }
            }
        }
    """ % (repository_owner, repository_name)
    result = query_github(query)
    try:
        d = result['data']['repository']
    except KeyError:
        return {}
    out = {}
    out['repository_owner'] = repository_owner
    out['repository_name'] = repository_name
    if d is None:
        print(f"Warning: not found: {repository_owner}/{repository_name}")
        return out
    for field in ['createdAt', 'pushedAt']:
        out[field] = d[field]
    if d['primaryLanguage'] is None:
        out['language'] = None
    else:
        out['language'] = d['primaryLanguage']['name']
    if d['licenseInfo'] is None:
        out['license'], out['pseudoLicense'] = None, None
    else:
        out['license'] = d['licenseInfo']['spdxId']
        out['pseudoLicense'] = d['licenseInfo']['pseudoLicense']
    out['n_forks'] = d['forks']['totalCount']
    out['n_stars'] = d['stargazers']['totalCount']
    out['n_pullRequests'] = d['pullRequests']['totalCount']
    out['n_issues'] = d['issues']['totalCount']
    return out


def build_authors_query(repository_owner="keplergo", repository_name="lightkurve",
                        contribution="pullRequests", first=100, after=None):
    """Build a GitHub GraphQL query which returns authors of a repo's issues or PRs.
    
    Returns
    -------
    query : str
        GraphQL query.
    """
    query = """
        query PRs {
            repository(owner:"%s", name:"%s") {
                %s(first:%s
        """ % (repository_owner, repository_name, contribution, first)
    if after is not None:
        query += ', after:"%s"' % after
    query += """) {
                    totalCount
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges() {
                        node() {
                            id
                            author {
                                login
                            }
                        } 
                    }
                }
            }
        }
    """
    return query    


def get_authors(repository_owner="keplergo", repository_name="lightkurve",
                contribution="pullRequests"):
    """Returns a list of all authors of a repo's issues or pull requests.
    
    Returns
    -------
    authors : list
        List of all GitHub usernames who opened a Pull Request on the repo.
    """
    authors = []
    # GitHub's GraphQL API only appears to allow retreiving 100 edges at a time;
    # so we are forced to paginate.
    endCursor, hasNextPage = None, True
    while hasNextPage:
        qry = build_authors_query(repository_owner=repository_owner,
                                  repository_name=repository_name,
                                  contribution=contribution,
                                  after=endCursor)
        js = query_github(qry)
        try:
            if js['data']['repository'] is None:
                print(f"Warning: not found: {repository_owner}/{repository_name}")
                return []
        except KeyError:
            return []
        extra_authors = [edge['node']['author']['login']
                         for edge in js['data']['repository'][contribution]['edges']
                         if edge['node']['author'] is not None]
        authors.extend(extra_authors)
        endCursor = js['data']['repository'][contribution]['pageInfo']['endCursor']
        hasNextPage = js['data']['repository'][contribution]['pageInfo']['hasNextPage']
    # Sanity check: did we get all authors?
    #assert(len(authors) == js['data']['repository'][contribution]['totalCount'])
    return authors


def get_repo_stats(repository_owner="keplergo", repository_name="lightkurve"):
    """Returns all repository stats we care about.
    
    Returns
    -------
    stats : dict
        Stats for the requested repo.
    """
    stats = get_easy_stats(repository_owner, repository_name)
    authors_issues = get_authors(repository_owner, repository_name, contribution="issues")
    authors_prs = get_authors(repository_owner, repository_name, contribution="pullRequests")
    stats['n_issues_unique_authors'] = len(np.unique(authors_issues))
    stats['n_prs_unique_authors'] = len(np.unique(authors_prs))
    stats['n_unique_authors'] = len(np.unique(authors_issues + authors_prs))
    return stats


if __name__ == "__main__":
    import pandas as pd
    import githubwebstats
    github_urls = list(githubwebstats._clean_github_urls())
    github_urls.append("github.com/KeplerGO/lightkurve")
    stats = []
    for url in tqdm(github_urls):
        components = url.split("/")
        stats.append(get_repo_stats(repository_owner=components[1],
                                    repository_name=components[2]))
    newdf = pd.DataFrame(stats)
    newdf.to_csv("github-api-stats.csv")
    print(get_rate_limit())
