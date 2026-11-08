#!/usr/bin/env python3
"""Render the 1200x630 social share cards and point each page's og:image at its card.

  python3 tools/og_cards.py [repo]

Cards come from the templates in tools/og/ (home.html, bugle.html, ai-<slug>.html),
screenshotted with headless Chrome into img/og/. Le Bugle cards read the issue number,
date and title from each issue page, so rerun this after renumbering (add_issue.py does).
Case studies keep their own product screenshots in img/cases/. Safe to rerun.
"""
import glob, html, os, re, subprocess, sys, tempfile, urllib.parse

SITE = 'https://pierresauvignon.github.io/'
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
os.chdir(root)
os.makedirs('img/og', exist_ok=True)


def render(template, out, params=None):
    url = 'file://' + os.path.abspath('tools/og/' + template)
    if params:
        url += '?' + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    with tempfile.TemporaryDirectory() as prof:
        tmp = os.path.join(prof, 'card.png')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                        '--user-data-dir=' + prof, '--force-device-scale-factor=1', '--window-size=1200,630',
                        '--virtual-time-budget=8000', '--screenshot=' + tmp, url],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        data = open(tmp, 'rb').read()
    # rewrite only when the pixels changed, so reruns leave git clean
    if not os.path.exists(out) or open(out, 'rb').read() != data:
        open(out, 'wb').write(data)
        print('rendered', out)


def point(page, card, alt, article=False):
    """Set og:image (+ size, alt), and on articles the BlogPosting JSON-LD image too."""
    t = open(page).read()
    img = SITE + card
    tags = ('<meta property="og:image" content="%s" />\n  <meta property="og:image:width" content="1200" />\n'
            '  <meta property="og:image:height" content="630" />\n  <meta property="og:image:alt" content="%s" />'
            % (img, html.escape(alt)))
    t, k = re.subn(r'<meta property="og:image" content="[^"]*" />(\s*<meta property="og:image:(width|height|alt)" content="[^"]*" />)*',
                   tags, t, count=1)
    assert k == 1, page
    if article:
        t = re.sub(r'"image": "%simg/[^"]*"' % re.escape(SITE), '"image": "%s"' % img, t)
    open(page, 'w').write(t)


# homepage
render('home.html', 'img/og/home.png')
point('index.html', 'img/og/home.png',
      'Pierre Sauvignon: I turn ideas into products people pay for. With his portrait')

# Le Bugle archive and every issue
issues = sorted(glob.glob('bugle/*/index.html'))
render('bugle.html', 'img/og/bugle.png', {'date': 'No. 1 to No. %d' % len(issues)})
point('bugle/index.html', 'img/og/bugle.png', 'Le Bugle, a weekly teleprinter tape from Pierre Sauvignon')
for page in issues:
    slug = page.split('/')[1]
    t = open(page).read()
    m = re.search(r'Le Bugle · No\. (\d+) · <time datetime="(\d{4})-(\d\d)-(\d\d)">', t)
    title = html.unescape(re.search(r'<h1>(.*?)</h1>', t, re.S).group(1))
    date = '%s %s %s' % (m.group(4), 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()[int(m.group(3)) - 1], m.group(2))
    card = 'img/og/bugle-%s.png' % slug
    render('bugle.html', card, {'n': m.group(1), 'date': date, 'title': title})
    point(page, card, 'Le Bugle No. %s on a teleprinter tape: %s' % (m.group(1), title), article=True)

# AI, explained articles: each has its own hand-made template tools/og/ai-<slug>.html
for page in sorted(glob.glob('ai/*/index.html')):
    slug = page.split('/')[1]
    if os.path.exists('tools/og/ai-%s.html' % slug):
        render('ai-%s.html' % slug, 'img/og/%s.png' % slug)
