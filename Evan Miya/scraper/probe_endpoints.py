import requests
from urllib.parse import urljoin

base = 'https://evanmiya.com/'
paths = [
    'team_ratings.csv', 'team_ratings.json', 'data/team_ratings.csv', 'data/team_ratings.json',
    'download/team_ratings.csv', 'download/team_ratings.json', 'downloads/team_ratings.csv',
    'api/team_ratings', 'api/team_ratings.json', '?team_ratings&download=1', '?download=team_ratings',
    '?download_team_ratings=1', '?format=csv&tab=team_ratings', 'assets/team_ratings.csv'
]

print('Probing endpoints on', base)
for p in paths:
    url = urljoin(base,p)
    try:
        r = requests.get(url, timeout=12)
        ct = r.headers.get('content-type','')
        print(url, r.status_code, ct)
        if r.ok and ('text/csv' in ct or 'application/json' in ct or '\n' in r.text[:200] or ',' in r.text[:200]):
            print('--- sample start ---')
            print(r.text[:800])
            print('--- sample end ---')
    except Exception as e:
        print('error', url, e)

# try triggering the page download param
try:
    r = requests.get('https://evanmiya.com/?team_ratings&download=team_ratings', timeout=12)
    print('\nprobe with download param:', r.status_code, r.headers.get('content-type'))
    print(r.text[:800])
except Exception as e:
    print('error probing download param', e)
