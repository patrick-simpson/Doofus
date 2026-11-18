# Doofus — `doofus.live`

An infinite live stream of an empty chair.

It looks like a serious, professional 24/7 broadcast: a LIVE badge, a viewer
counter that drifts and gets raided, a scrolling chat, breaking-news crawls,
buffering hiccups, signal drops, "are you still watching?" nags, and an absurd
multi-year uptime. None of it ever resolves. The picture never changes. Nothing
happens, on purpose. The punchline is the silence.

## How it works

The entire site is **one file** — [`index.html`](./index.html). No build step,
no dependencies, no bundler, no framework. Open it in a browser and it runs.
Everything you see is generated client-side from a handful of constants and
copy arrays:

- **Visuals** are CSS, styled as a small public-access TV station: an ON AIR
  sign, a solid-block lower-third, a station bug, a yellow bulletin ticker,
  SMPTE color bars on the cold open, CRT scanlines. Hard edges, no glow.
- **Type** is Archivo (its width axis supplies the condensed broadcast
  headlines) and IBM Plex Mono for the engineering readouts, both from
  Google Fonts with system fallbacks.
- **Behavior** (chat, viewer drift, telemetry, theater, toasts, idle nag,
  Konami easter egg) is vanilla ES6 organized into small self-contained
  modules at the bottom of the file.
- The **room tone** is a refrigerator hum synthesized with the Web Audio API,
  and the **favicon** is drawn on a `<canvas>` at runtime — so there are no
  asset files to manage.

The stream image is [`chair.svg`](./chair.svg), a wooden chair in a spare room
seen from a fixed, slightly elevated camera. It isn't hand-drawn: it's built
by [`tools/make_chair.py`](./tools/make_chair.py), which models the chair as a
few 3D boxes, projects them through a pinhole camera, shades each face from a
single window light, and casts the shadow onto the floor. To move the camera,
change the wood, or swap the light, edit the constants at the top and run:

```sh
python3 tools/make_chair.py > chair.svg
```

`og-image.jpg` is a raster render of the same frame for link previews (most
social sites won't unfurl an SVG). If `chair.svg` ever fails to load, an inline
SVG chair in the script takes over so the joke can't break.

## Running it

```sh
# Just open the file:
open index.html            # macOS  (xdg-open on Linux)

# …or serve it, which is closer to production:
python3 -m http.server
# then visit http://localhost:8000
```

## Reskinning the joke

You change the whole bit by editing the **`CONFIG` block** and the **copy
arrays** near the top of the `<script>` in `index.html` — that is the single
intended edit point:

- `CONFIG.STREAM_IMAGE_URL` — the subject of the broadcast (the source of
  truth; the `<img src>` in the markup is just the pre-JS fallback).
- `CONFIG.SUBJECT` — the noun used throughout the copy.
- `CONFIG.viewers` / `CONFIG.timing` — pacing of the counter and the gags.
- The arrays — `CHAT_LINES`, `BREAKING_LINES`, `ACHIEVEMENTS`, `CHYRON_PLACES`,
  `WATCH_REGIONS`, `RAID_PARTIES`, `SUPERCHATS`, `IMPATIENT_LINES`, `EMOTES` —
  are the writing. Keep the tone dry and the cadence slow; restraint is the
  joke.

## Deploying

Static hosting. This repo is set up for **GitHub Pages** with a custom domain
via the [`CNAME`](./CNAME) file (`doofus.live`). Pushing to the published
branch is the deploy.

## Lint

A minimal HTMLHint check runs in CI on pull requests
([`.github/workflows/lint.yml`](./.github/workflows/lint.yml)). To run it
locally:

```sh
npx htmlhint index.html
```
