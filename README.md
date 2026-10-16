# pierresauvignon.github.io

Personal site of Pierre Sauvignon, live at **https://pierresauvignon.github.io**.

A one-page résumé plus a case study for each product I've designed, built and run solo:

| Product | What it is | Case study |
|---|---|---|
| LobsterOne | Analytics for AI coding tools: a Mac menu bar app and web dashboard | [/lobsterone/](https://pierresauvignon.github.io/lobsterone/) |
| TigerSoup | A Mac app that sets up a production-grade project in under a minute | [/tigersoup/](https://pierresauvignon.github.io/tigersoup/) |
| OnReplay | Turns a handful of photos into an AI-animated short film | [/onreplay/](https://pierresauvignon.github.io/onreplay/) |
| OnSilent | An AI receptionist for Australian tradespeople and real-estate agents | [/onsilent/](https://pierresauvignon.github.io/onsilent/) |

## How it's built

Plain static HTML and CSS, served by GitHub Pages from `master`. There is no build step, framework or JavaScript dependency.

```
index.html            Homepage: intro, experience, "Building now" cards, photos, contact
css/case-study.css    Shared styles for the case-study pages
<product>/index.html  One case study per product
icons/                Product icons
img/                  Photos, plus img/cases/ for product screenshots
```

- **Theming:** colours are CSS custom properties on `:root`, with a dark mode that follows the system setting. Each case study sets its own `--accent`.
- **Diagrams and charts:** inline SVG that uses the same colour tokens, so they switch with dark mode.
- **Fonts:** Onest and Geist Mono from Google Fonts.

## Run locally

```sh
python3 -m http.server 8765
```

Then open http://localhost:8765.

## Deploy

Push to `master`. GitHub Pages publishes within a minute or two.
