#!/usr/bin/env python3
import os
import requests

TOKEN    = os.environ['GH_TOKEN']
USERNAME = 'DHEENA0007'
HEADERS  = {'Authorization': f'bearer {TOKEN}', 'Content-Type': 'application/json'}
GQL      = 'https://api.github.com/graphql'

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
    }
    repositories(first: 100, ownerAffiliations: OWNER) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
  }
}
"""

def fetch():
    r = requests.post(GQL, json={'query': QUERY, 'variables': {'login': USERNAME}}, headers=HEADERS)
    return r.json()['data']['user']

def stats_svg(data):
    repos   = data['repositories']['nodes']
    contrib = data['contributionsCollection']
    stars   = sum(r['stargazerCount'] for r in repos)
    forks   = sum(r['forkCount'] for r in repos)
    total   = data['repositories']['totalCount']
    commits = contrib['totalCommitContributions']
    prs     = contrib['totalPullRequestContributions']
    issues  = contrib['totalIssueContributions']

    def stat_block(x, label, icon, value):
        return f'''
  <text x="{x}" y="78" font-family="Segoe UI,sans-serif" font-size="11" fill="#888">{icon} {label}</text>
  <text x="{x}" y="104" font-family="Segoe UI,sans-serif" font-size="26" font-weight="700" fill="#212121">{value:,}</text>'''

    def stat_block2(x, label, icon, value):
        return f'''
  <text x="{x}" y="148" font-family="Segoe UI,sans-serif" font-size="11" fill="#888">{icon} {label}</text>
  <text x="{x}" y="174" font-family="Segoe UI,sans-serif" font-size="26" font-weight="700" fill="#212121">{value:,}</text>'''

    return f'''<svg width="495" height="200" viewBox="0 0 495 200" xmlns="http://www.w3.org/2000/svg">
  <rect width="495" height="200" rx="12" fill="white" stroke="#eeeeee" stroke-width="1.5"/>
  <rect width="495" height="46" rx="12" fill="#FFF3EF"/>
  <rect y="34" width="495" height="12" fill="#FFF3EF"/>
  <text x="20" y="30" font-family="Segoe UI,sans-serif" font-size="15" font-weight="700" fill="#FF5722">📊 Dheena's GitHub Stats</text>
  {stat_block(20,  "Total Stars",  "⭐", stars)}
  {stat_block(185, "Commits",      "📝", commits)}
  {stat_block(350, "Public Repos", "📁", total)}
  <line x1="20" y1="122" x2="475" y2="122" stroke="#f0f0f0" stroke-width="1"/>
  {stat_block2(20,  "Pull Requests", "🔀", prs)}
  {stat_block2(185, "Issues",        "🐛", issues)}
  {stat_block2(350, "Forks",         "🍴", forks)}
</svg>'''

def langs_svg(data):
    repos = data['repositories']['nodes']
    sizes = {}
    for repo in repos:
        for edge in repo['languages']['edges']:
            n = edge['node']['name']
            c = edge['node']['color'] or '#858585'
            s = edge['size']
            if n not in sizes:
                sizes[n] = {'size': 0, 'color': c}
            sizes[n]['size'] += s

    top = sorted(sizes.items(), key=lambda x: x[1]['size'], reverse=True)[:7]
    if not top:
        return ''

    total = sum(v['size'] for _, v in top)
    h     = 70 + len(top) * 36 + 20

    bar_svg = ''
    x = 20
    for lang, info in top:
        w = max(1, 455 * info['size'] / total)
        bar_svg += f'<rect x="{x:.1f}" y="58" width="{w:.1f}" height="12" fill="{info["color"]}" rx="2"/>'
        x += w

    rows = ''
    for i, (lang, info) in enumerate(top):
        pct  = info['size'] / total * 100
        y    = 98 + i * 36
        bw   = int(400 * pct / 100)
        rows += f'''
  <circle cx="30" cy="{y}" r="6" fill="{info['color']}"/>
  <text x="46" y="{y+5}" font-family="Segoe UI,sans-serif" font-size="13" font-weight="600" fill="#212121">{lang}</text>
  <text x="475" y="{y+5}" font-family="Segoe UI,sans-serif" font-size="12" fill="#888" text-anchor="end">{pct:.1f}%</text>
  <rect x="46" y="{y+10}" width="{bw}" height="4" fill="{info['color']}" rx="2" opacity="0.35"/>'''

    return f'''<svg width="495" height="{h}" viewBox="0 0 495 {h}" xmlns="http://www.w3.org/2000/svg">
  <rect width="495" height="{h}" rx="12" fill="white" stroke="#eeeeee" stroke-width="1.5"/>
  <rect width="495" height="46" rx="12" fill="#FFF3EF"/>
  <rect y="34" width="495" height="12" fill="#FFF3EF"/>
  <text x="20" y="30" font-family="Segoe UI,sans-serif" font-size="15" font-weight="700" fill="#FF5722">💻 Most Used Languages</text>
  {bar_svg}
  {rows}
</svg>'''

def main():
    os.makedirs('assets', exist_ok=True)
    data = fetch()
    with open('assets/stats.svg', 'w') as f:
        f.write(stats_svg(data))
    with open('assets/langs.svg', 'w') as f:
        f.write(langs_svg(data))
    print('✅ SVGs generated')

if __name__ == '__main__':
    main()
