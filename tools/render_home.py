"""Rebuild the homepage Le Bugle column (latest issue as a strip of wire tape with its archive summary, + 3 earlier issues as a log) from bugle/index.html.

usage: python3 render_home.py SITE_DIR
"""
import re, html, os, sys, datetime


def render(site):
    archive = open(os.path.join(site, 'bugle/index.html')).read()
    rows = re.findall(r'<li><a href="([^"/]+)/"><span class="meta"><b>No\. (\d+)</b><time datetime="([\d-]+)">.*?<h2>(.*?)</h2><p>(.*?)</p>', archive, re.S)
    rows.sort(key=lambda r: r[2], reverse=True)
    (slug, num, date, title, summary), earlier = rows[0], rows[1:4]
    post = open(os.path.join(site, 'bugle/%s/index.html' % slug)).read()
    mins = re.search(r'· (\d+) min read', post).group(1)
    d = datetime.date.fromisoformat(date)
    log = ''.join(
        '\n    <a href="bugle/%s/"><small><b>No. %s</b> · %d %s</small><span>%s</span></a>'
        % (s, n, datetime.date.fromisoformat(dt).day, datetime.date.fromisoformat(dt).strftime('%b'), t)
        for s, n, dt, t, _ in earlier)
    block = '''<!-- bugle:start -->
   <article class="lb-tape">
    <div class="lb-meta"><span><b>No. %s</b> · Perth WA</span><time datetime="%s">%02d %s</time></div>
    <h3><a href="bugle/%s/">%s</a></h3>
    <p>%s</p>
    <div class="lb-ft"><a class="lb-go" href="bugle/%s/">Read this week’s issue <b>→</b></a><span>%s min read</span></div>
   </article>
   <nav class="lb-list" aria-label="Earlier issues">%s
   </nav>
   <!-- bugle:end -->''' % (num, date, d.day, d.strftime('%b %Y'), slug, title, summary, slug, mins, log)
    p = os.path.join(site, 'index.html')
    h = open(p).read()
    h, k = re.subn(r'<!-- bugle:start -->.*?<!-- bugle:end -->', lambda m: block, h, count=1, flags=re.S)
    assert k == 1
    open(p, 'w').write(h)


if __name__ == '__main__':
    render(sys.argv[1])
