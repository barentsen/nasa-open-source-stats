import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
from copy import deepcopy

def _clean(string):
    bad_strs = ['\n', '. ', ')', '(', ',']
    newstring = deepcopy(string)
    for b in bad_strs:
        newstring = newstring.replace(b, '')
    return newstring

def _clean_github_urls(filename='arxiv2github.csv'):
    df = pd.read_csv(filename)
    github_urls = []
    for idx, d in df.iterrows():
        urls = (d['urls'].replace("'", "")[1:-1].split(" "))
        if urls[0] == '':
            continue
        usernames = (np.unique([url.split('/')[1] for url in urls]))
        packages = ((np.unique([_clean('/'.join(url.split('/')[1:3])) for url in urls])))
        packages = np.unique(packages[packages != ''])
        packages = packages[['/' in package for package in packages]]

        ok = [len(package.split('/')[1].replace(' ', '')) > 0 for package in packages]
        packages = packages[ok]

        _ = [github_urls.append('github.com/{}'.format(package.lower())) for package in packages]

    github_urls = np.unique(github_urls)
    return github_urls


def github2stats(github_urls=_clean_github_urls()):
    results = pd.DataFrame(columns=['github_url', 'exists', 'readme',
                                    'readme_length', 'installation', "CI", "docs", 'fancy_docs',
                                    'examples', 'requirements', 'setup'])

    for idx in tqdm(range(len(github_urls))):
        github_url = github_urls[idx]
        results.loc[idx, 'github_url'] = github_url

        # Exists
        results.loc[idx, 'exists'] = requests.get('https://{}'.format(github_url), timeout=500).status_code == 200

        if results.loc[idx, 'exists']:

            # Has readme
            readme = None
            for name in ['README', 'readme']:
                for extension in ['.md', '.rst', '', '.txt']:
                    url = 'http://raw.{}/master/{}{}'.format(github_url, name, extension)
                    print(url)
                    response = requests.get(url, timeout=500)
                    if response.status_code == 200:
                        readme =  str(response.content, 'utf-8')
                        break
            if readme is not None:
                results.loc[idx, 'readme'] = True
                results.loc[idx, 'readme_length'] = len(readme)


            # Has installation
            print('https://raw.githubusercontent.com{}/master/setup.py'.format('/'.join(github_url.split('/')[1:]))
            response = requests.get('https://raw.githubusercontent.com{}/master/setup.py'.format('/'.join(github_url.split('/')[1:])), timeout=500)
            if response.status_code == 200:
                results.loc[idx, 'requirements'] =  True
            for file in ['INSTALL', 'makefile']:
                url = 'http://raw.{}/master/{}'.format(github_url, file)
                response = requests.get(url, timeout=500)
                if response.status_code == 200:
                    results.loc[idx, 'installation'] =  True
                    break
            if readme is not None:
                results.loc[idx, 'installation'] = np.asarray([term in readme.lower() for term in
                                                               ['pip ', 'install ', 'installation ',
                                                                ' installation instructions ', 'pypi',
                                                                'conda ']]).any()


            # Has CI
            for file in ['.travis.yml', 'azure-pipelines.yml', 'appveyor.yml', '.circleci/config.yml']:
                url = 'http://raw.{}/master/{}'.format(github_url, file)
                response = requests.get(url, timeout=500)
                if response.status_code == 200:
                    results.loc[idx, 'CI'] =  True
                    break


            # Has Docs
            docs = None
            for dir in ['doc', 'docs', 'documentation', 'document', 'documents', 'Documentation', "Docs"]:
                response = requests.get('http://{}/tree/master/{}'.format(github_url, dir), timeout=500)
                if response.status_code == 200:
                    results.loc[idx, 'docs'] =  True
                    docs = 'http://{}/tree/master/{}'.format(github_url, dir)
                    break


            # Has fancy docs
            url = 'http://{}.github.io/{}'.format(github_url.split('/')[1], github_url.split('/')[2])
            response = requests.get(url, timeout=500)
            if response.status_code == 200:
                results.loc[idx, 'fancy_docs'] = True
            if (results.loc[idx, 'fancy_docs'] != True) & (readme is not None):
                if 'readthedocs' in readme.lower():
                    results.loc[idx, 'fancy_docs'] = True


            # Has examples
            for dir in ['examples', 'tutorials', 'example', 'tutorial']:
                response = requests.get('http://{}/tree/master/{}'.format(github_url, dir), timeout=500)
                if response.status_code == 200:
                    results.loc[idx, 'examples'] =  True
                    break
            if (results.loc[idx, 'examples'] != True) & (docs is not None):
                # Has examples
                for dir in ['examples', 'tutorials', 'example', 'tutorial']:
                    response = requests.get('{}/{}'.format(docs, dir), timeout=500)
                    if response.status_code == 200:
                        results.loc[idx, 'examples'] =  True
                        break
            if (results.loc[idx, 'examples'] != True) & (readme is not None):
                for keyword in ['tutorials', 'examples']:
                    if keyword in readme.lower():
                        results.loc[idx, 'examples'] = True


            # Has Requirements
            response = requests.get('https://raw.{}/master/requirements.txt'.format(github_url), timeout=500)
            if response.status_code == 200:
                results.loc[idx, 'requirements'] =  True



    return results.fillna(False)
