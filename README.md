# The World Today — Saturday 21 November 2026 in one image

Entry for make.fun's **news-image-20261121** bounty ("Sum up 21 November's
world news in one image").

`main.py` is a pure Python 3 standard-library program: it draws a newspaper
front page of Saturday 21 November 2026 entirely in code — its own 5x7
bitmap font and rasteriser, no external assets, no network — and writes it
to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`). Two runs
write byte-identical files.

The front page:

- **Lead — War in Europe:** Russia's biggest bombardment of November
  (404 drones, 111 missiles) hits Ukraine; two missiles and a drone come
  down in Poland. Tusk: an intentional provocation. Rutte: a grave
  violation.
- **Markets:** AI sell-off tips Wall Street into correction.
- **Climate:** COP31 talks in Antalya run past the deadline on fossil fuels.
- **Europe:** UK and EU sign their biggest post-Brexit deal.
- **Health:** the daraxonrasib pill makes pancreatic tumours vanish in trial.
- **Iraq:** fire at the Basra (Hartha) power station kills four.
- Ticker: Mongolia's president resigns; EU defence aid for Ukraine; Iran's
  MQ-9 claim; Harden's 51 points.

Every story was cross-checked across at least two independent news sources
reporting 21 November 2026; the sources are listed in `main.py`'s docstring.

Run it:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

License: MIT (see `LICENSE`).
