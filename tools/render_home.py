"""Rebuild the homepage Le Bugle front page (latest issue as lead story + 3 earlier issues) from bugle/index.html.

usage: python3 render_home.py SITE_DIR
"""
import re, html, os, sys, datetime


def render(site):
    archive = open(os.path.join(site, 'bugle/index.html')).read()
    rows = re.findall(r'<li><a href="([^"/]+)/"><span class="meta"><b>No\. (\d+)</b><time datetime="([\d-]+)">.*?<h2>(.*?)</h2>', archive, re.S)
    rows.sort(key=lambda r: r[2], reverse=True)
    (slug, num, date, title), earlier = rows[0], rows[1:4]
    post = open(os.path.join(site, 'bugle/%s/index.html' % slug)).read()
    first_p = re.search(r'<article class="post">\s*<p>(.*?)</p>', post, re.S).group(1)
    text = html.unescape(re.sub(r'<[^>]+>', '', first_p))
    m = re.match(r'(.+?[.!?]["”]?)(?:\s|$)', text, re.S)
    lede = m.group(1) if m else text
    mins = re.search(r'· (\d+) min read', post).group(1)
    d = datetime.date.fromisoformat(date)
    side = ''.join(
        '\n    <a href="bugle/%s/"><small>No. %s · %d %s</small><strong>%s</strong></a>'
        % (s, n, datetime.date.fromisoformat(dt).day, datetime.date.fromisoformat(dt).strftime('%b'), t)
        for s, n, dt, t in earlier)
    block = '''<article class="fp">
   <div class="fp-mast"><span>No. %s</span><b>Le Bugle</b><span>Perth, WA</span></div>
   <div class="fp-strap"><time datetime="%s">%s %d %s</time><span>Weekly · tech &amp; AI</span></div>
   <div class="fp-body">
    <div class="fp-lead">
     <span class="fp-kick">This week</span>
     <h3><a href="bugle/%s/">%s</a></h3>
     <p>%s</p>
     <div class="fp-foot"><a class="go" href="bugle/%s/">Read this week’s issue <b>→</b></a><span>%s min read</span></div>
    </div>
    <aside class="fp-side" aria-label="Earlier issues"><h4>Earlier issues</h4>%s
    </aside>
   </div>
  </article>''' % (num, date, d.strftime('%A'), d.day, d.strftime('%B %Y'), slug, title,
                   html.escape(lede, quote=False), slug, mins, side)
    p = os.path.join(site, 'index.html')
    h = open(p).read()
    h, k = re.subn(r'<article class="(?:clip|fp)">.*?</article>', lambda m: block, h, count=1, flags=re.S)
    assert k == 1
    open(p, 'w').write(h)


if __name__ == '__main__':
    render(sys.argv[1])
