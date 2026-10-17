#!/usr/bin/env python3
"""Generate repository-owned GitHub cards from public API data. No dependencies."""

from collections import Counter
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets'
USER = '3z4k'
COLORS = {'EJS':'#d9957d','JavaScript':'#d7c49a','Python':'#79b3c8',
          'HTML':'#bc8e9d','CSS':'#9c9bc2','TypeScript':'#80b7bc'}


def api(path):
    headers = {'Accept':'application/vnd.github+json','User-Agent':'3z4k-profile',
               'X-GitHub-Api-Version':'2022-11-28'}
    token = os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer '+token
    with urlopen(Request('https://api.github.com/'+path,headers=headers),timeout=30) as response:
        return json.load(response)


def text(x,y,value,size=14,color='#d9ecec'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}">{escape(str(value))}</text>'


def card(title,description,body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="540" height="196" viewBox="0 0 540 196" role="img">'
            f'<title>{escape(title)}</title><desc>{escape(description)}</desc>'
            '<rect x="1" y="1" width="538" height="194" rx="12" fill="#08131c" stroke="#263e4b"/>'
            '<g font-family="ui-monospace, SFMono-Regular, Consolas, monospace">'+body+'</g></svg>')


def main():
    user = api('users/'+USER)
    repos = []
    page = 1
    while True:
        batch = api(f'users/{USER}/repos?per_page=100&type=owner&page={page}')
        repos.extend(r for r in batch if not r['private'])
        if len(batch) < 100:
            break
        page += 1
    original = [r for r in repos if not r['fork']]
    languages = Counter()
    for repo in original:
        # The profile's own artwork generator should not dominate the project mix.
        if repo['name'].lower() != USER:
            languages.update(api(f"repos/{USER}/{repo['name']}/languages"))
    updated = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    stats = [(user['public_repos'],'public repos'),(user['followers'],'followers'),
             (sum(r['forks_count'] for r in original),'project forks')]
    body = text(25,34,'$ github / '+USER,15,'#85b5c4')
    for x,(value,label) in zip((25,203,381),stats):
        body += text(x,98,value,36)+text(x,124,label,12,'#8da8b5')
    body += text(25,173,'here since '+user['created_at'][:4],11,'#8da8b5')
    body += text(348,173,'updated '+updated,10,'#8da8b5')
    OUT.mkdir(exist_ok=True)
    (OUT/'github.svg').write_text(card('GitHub profile stats',
        ', '.join(f'{v} {label}' for v,label in stats),body))
    body = text(25,34,'$ languages / public projects',15,'#85b5c4')
    most = languages.most_common(5)
    total = sum(languages.values())
    x = 25
    if total:
        for name,count in most:
            width = 490*count/total
            color = COLORS.get(name,'#8da8b5')
            body += f'<rect x="{x:.2f}" y="65" width="{width:.2f}" height="7" fill="{color}"/>'
            x += width
        y = 105
        for index,(name,count) in enumerate(most):
            col = index%2
            row = index//2
            px,py = 25+col*245,y+row*23
            body += text(px,py,'●',12,COLORS.get(name,'#8da8b5'))
            body += text(px+19,py,f'{name}  {count/total:.1%}',12)
    else:
        body += text(25,105,'new code on the horizon.',14)
    body += text(25,173,'by code size / original repos',11,'#8da8b5')
    (OUT/'languages.svg').write_text(card('Public project languages',
        ', '.join(f'{name} {count/total:.1%}' for name,count in most),body))
    print('Updated public GitHub profile and language cards.')


if __name__ == '__main__':
    main()
