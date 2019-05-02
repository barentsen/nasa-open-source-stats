"""Find a set of arXiv identifiers given a NASA ADS literature query!"""

def get_arxiv_ids(ads_query="full:'github.com' Kepler"):
    """Returns arXiv identifiers of papers given an ADS query.

    For this to work, you need to do two things:
    1. `pip install ads`
    2. Get a ADS developer key from https://ui.adsabs.harvard.edu/user/settings/token
    and store it in `~/.ads/dev_key `.
    """
    import ads
    out_identifiers, out_citations = [], []
    qry = ads.SearchQuery(q=ads_query,
                        fl=['identifier', 'citation_count'],
                        rows=9999999999)  # the default is something low
    for paper in qry:
        for identifier in paper.identifier:
            if 'arXiv:' in identifier:
                out_identifiers.append(identifier)
                out_citations.append(paper.citation_count)
    return out_identifiers, out_citations


if __name__ == "__main__":
    # Example use
    ids, citations = get_arxiv_ids()
    print(ids)
