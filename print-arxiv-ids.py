def get_arxiv_ids(ads_query="full:'github.com' Kepler")
    """Returns arXiv identifiers of papers given an ADS query.

    For this to work, you need to `pip install ads` and also make sure
    to store your ADS developer key in `~/.ads/dev_key `.
    You can get an ADS key from https://ui.adsabs.harvard.edu/user/settings/token.
    """
    import ads
    out_identifiers, out_citations = [], []
    qry = ads.SearchQuery(q=ads_query,
                        fl=['identifier', 'citation_count'],
                        rows=9999999999)
    for paper in qry:
        for identifier in paper.identifier:
            if 'arXiv:' in identifier:
                out_identifiers.append(identifier)
                out_citations.append(paper.citation_count)



if __name__ == "__main__":
    ids, citations = get_arxiv_ids()
    print(ids)
