"""Add a Le Bugle issue to the site and renumber every issue by date (oldest = No. 1).

usage: python3 tools/add_issue.py . POST.md SLUG YYYY-MM-DD "Full title" "Short title" "Summary sentence."
POST.md holds the body only (no "# title" line), paragraphs separated by blank lines, [text](url) links.
"""
import re, html, os, sys, datetime

site, md_path, slug, date, title, short, summary = sys.argv[1:8]
md_path = os.path.abspath(md_path)
os.chdir(site)
md = open(md_path).read().strip()
if md.startswith('# '):
    md = md.split('\n', 1)[1].strip()


def conv(par):
    out, pos = [], 0
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', par):
        out.append(html.escape(par[pos:m.start()], quote=False))
        out.append('<a href="%s">%s</a>' % (html.escape(m.group(2)), html.escape(m.group(1), quote=False)))
        pos = m.end()
    out.append(html.escape(par[pos:], quote=False))
    return '<p>' + ''.join(out) + '</p>'


paras = [p.strip() for p in md.split('\n\n') if p.strip()]
body = '\n\n'.join(conv(p) for p in paras)
words = len(re.sub(r'\]\([^)]*\)', '', md).split())
mins = max(1, round(words / 200))
d = datetime.date.fromisoformat(date)
long_date = '%d %s' % (d.day, d.strftime('%B %Y'))
short_date = '%d %s' % (d.day, d.strftime('%b %Y'))
esc = lambda s: html.escape(s, quote=False).replace('"', '&quot;')
plain_summary = summary.replace('’', "'")

# --- new post page, from the template of an existing one ---
archive = open('bugle/index.html').read()
items = re.findall(r'<li><a href="([^"/]+)/">.*?<time datetime="([\d-]+)">.*?</li>', archive, re.S)
assert slug not in [s for s, _ in items], 'slug exists'
tpl_slug = items[0][0]
s = open('bugle/%s/index.html' % tpl_slug).read()
old_title = html.unescape(re.search(r'<h1>(.*?)</h1>', s).group(1))
old_short = re.search(r'<title>(.*?) · Le Bugle', s).group(1)
old_crumb = re.search(r'"position": 3, "name": "([^"]*)"', s).group(1)
old_desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
old_date = re.search(r'<time datetime="([\d-]+)">(.*?)</time>', s)
lead = plain_summary.split(' ', 1)[0]
desc_body = plain_summary[0].lower() + plain_summary[1:] if lead in ('A', 'An', 'The', 'Why', 'How', 'What', 'Two', 'Three') else plain_summary
s = s.replace(old_desc, esc('Le Bugle No. 1: ' + desc_body))
s = s.replace('<title>%s · Le Bugle' % old_short, '<title>%s · Le Bugle' % esc(short))
s = s.replace('"position": 3, "name": "%s"' % old_crumb, '"position": 3, "name": "%s"' % short.replace('"', '\\"'))
s = s.replace(esc(old_title), esc(title)).replace(old_title, title)
s = s.replace(tpl_slug, slug).replace(old_date.group(1), date).replace(old_date.group(2), long_date)
s = re.sub(r' · \d+ min read', ' · %d min read' % mins, s)
s = re.sub(r'<article class="post">.*?</article>', lambda m: '<article class="post">\n' + body + '\n</article>', s, flags=re.S)
assert old_title not in s and old_date.group(1) not in s
os.makedirs('bugle/' + slug, exist_ok=True)
open('bugle/%s/index.html' % slug, 'w').write(s)

# --- archive: insert, sort newest first ---
li = ('  <li><a href="%s/"><span class="meta"><b>No. 0</b><time datetime="%s">%s</time></span><div><h2>%s</h2><p>%s</p></div></a></li>'
      % (slug, date, short_date, esc(title), esc(summary)))
lis = re.findall(r'  <li>.*?</li>', archive, re.S) + [li]
lis.sort(key=lambda x: re.search(r'datetime="([\d-]+)"', x).group(1), reverse=True)
archive = re.sub(r'(<ul class="issues">\n).*?(</ul>)', lambda m: m.group(1) + '\n'.join(lis) + '\n' + m.group(2), archive, flags=re.S)

# --- renumber posts, rebuild previous/next ---
issues = sorted(items + [(slug, date)], key=lambda x: x[1])
for i, (sl, dt) in enumerate(issues):
    n = i + 1
    f = 'bugle/%s/index.html' % sl
    t = open(f).read()
    t = re.sub(r'Le Bugle No\. \d+:', 'Le Bugle No. %d:' % n, t)
    t = re.sub(r'Le Bugle · No\. \d+ ·', 'Le Bugle · No. %d ·' % n, t)
    links = []
    if i > 0: links.append('<a href="../%s/">← Previous issue</a>' % issues[i - 1][0])
    links.append('<a href="../">All issues</a>')
    if i < len(issues) - 1: links.append('<a href="../%s/">Next issue →</a>' % issues[i + 1][0])
    t, k = re.subn(r'<div class="next">.*?</div>', '<div class="next">' + ''.join(links) + '</div>', t, count=1, flags=re.S)
    assert k == 1
    open(f, 'w').write(t)
    archive, k = re.subn(r'<b>No\. \d+</b><time datetime="%s">' % dt, '<b>No. %d</b><time datetime="%s">' % (n, dt), archive)
    assert k == 1
open('bugle/index.html', 'w').write(archive)

# --- homepage front page: lead story and earlier issues come from the archive ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_home
render_home.render('.')

# --- sitemap and llms.txt ---
x = open('sitemap.xml').read()
open('sitemap.xml', 'w').write(x.replace('</urlset>', '  <url><loc>https://pierresauvignon.github.io/bugle/%s/</loc><lastmod>%s</lastmod></url>\n</urlset>' % (slug, date)))
x = open('llms.txt').read()
bullets = re.findall(r'^- \[.*\]\(https://pierresauvignon\.github\.io/bugle/[^)]+\) \(.*\)$', x, re.M)
new_b = '- [%s](https://pierresauvignon.github.io/bugle/%s/) (%s)' % (title, slug, long_date)
allb = bullets + [new_b]
key = lambda b: datetime.datetime.strptime(re.search(r'\((\d+ \w+ \d{4})\)$', b).group(1), '%d %B %Y')
allb.sort(key=key, reverse=True)
x = x.replace('\n'.join(bullets), '\n'.join(allb))
open('llms.txt', 'w').write(x)

print('%d words, %d min, %d links, %d paragraphs, now %d issues (this is No. %d)'
      % (words, mins, body.count('<a href'), len(paras), len(issues), [s for s, _ in issues].index(slug) + 1))
