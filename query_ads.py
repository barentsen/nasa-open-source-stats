"""Find a set of arXiv identifiers given a NASA ADS literature query!"""
import pandas as pd

# Which fields do we want from the ADS API?
FIELDS = ['ack', 'aff', 'arxiv_class', 'author', 'bibcode', 'bibgroup', 'bibstem',
          'citation_count', 'data', 'database', 'first_author', 'grant',
          'identifier', 'keyword', 'property', 'pubdate', 'read_count',
          'title', 'vizier', 'year']

def query_ads(query="full:'github.com' Kepler"):
    """Returns a list of dictionary objects, one per paper.

    For this to work, you need to do two things:
    1. `pip install ads`
    2. Get a ADS developer key from https://ui.adsabs.harvard.edu/user/settings/token
    and store it in `~/.ads/dev_key `.
    """
    import ads
    result = []
    qry = ads.SearchQuery(q=query, fl=FIELDS, rows=9999999999)
    for paper in qry:
        mydict = paper._raw
        mydict['arxiv_id'] = None
        for identifier in paper.identifier:
            if 'arXiv:' in identifier:
                mydict['arxiv_id'] = identifier
        result.append(mydict)
    return result


if __name__ == "__main__":
    # Example use
    papers = query_ads()
    df = pd.DataFrame(papers)
    df.to_csv("papers.csv")
