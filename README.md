# Basque Tables

A directory of Basque dining rooms in **California, Nevada and Idaho** — with, for two
people deciding where to eat, the four facts that settle it: how the house seats you,
what dinner costs, which nights the door opens, and whether the bar makes a Picon Punch.

**→ https://nanobotco.github.io/basque-tables/**

84 records · 28 rooms · 200 pages · 110 freely-licensed pictures · English and Euskara.

## The rule the whole thing is built on

**Three states, never two.** A day in `hours.open` is open. A day in `hours.closed` is
closed. A day in neither is **not published** — it draws as a dashed box, and it is
excluded from every filter rather than guessed either way. The same goes for seating and
for the Picon: `unknown` is a value, not a blank.

And the validator refuses to let `seating`, `picon`, `prices`, `hours`, `status` or
`address` rest on tier `tradition` or `inference`. Somebody drives to those.

## What it does not do

It does not rank rooms, and it never calls one romantic. It prints the fields and the
source for each one. Where the sources disagree, both are recorded and neither is
settled. Where nothing is published, the page says so — 75 open questions are listed on
[/gaps/](https://nanobotco.github.io/basque-tables/gaps/), each naming its record.

## Some of what is in it

- **The long table.** A Basque dining room in the West is a boarding house that outlived
  its boarders, and a boarding house seats everybody at one table. Eight rooms still do.
  Thirteen give two people a table of their own.
- **The Basque Block**, Boise: a pub, a market, a dining room, a club and a museum on one
  block of Grove Street — and the museum is inside the 1864 boarding house the rest grew
  around, which took Basque boarders until 1969.
- **The Picon Punch**, which was invented in the American West, is barely drunk in the
  Basque Country, became Nevada's state cocktail in 2025, and is built on a French bitter
  that has never been reliably imported.
- **Euskara**: the interface is translated at `/eu/`. The write-ups are not, and the page
  says why — no English-to-Basque machine translator was available.

## Running it

Python 3 standard library only. No framework, no database, no webfont, no CDN, no tracking.

```
python3 tools/validate.py     refuse anything the site should not publish
python3 tools/build.py        counts, kin backlinks, price and hours tables, search docs
python3 tools/site.py         write build/
python3 tools/serve.py        look at it on http://localhost:8802/
python3 tests/test_all.py     run before any publish
./publish.sh                  validate, build, test, copy into docs/
```

`README.txt` is the working guide and `AUTHORING.txt` explains how to write a record.

## Licence

Layered on purpose — see [LICENSE](LICENSE) and [NOTICE.txt](NOTICE.txt). Records CC BY 4.0; **every picture carries
its own licence in a sidecar `.json` beside it** (CC0, public domain, CC BY, CC BY-SA or
FAL, and the credit prints on every page); code MIT.

**Using it.** Attribution is the whole of the condition — copy it, adapt it,
sell it, index it, train on it, and say where it came from.
[Open an issue](https://github.com/NaNoBotCo/basque-tables/issues) if something is missing.

---

Contact: Nan · nan@motdang.net · Sponsor: [Ko-fi](https://ko-fi.com/defiantchiangmai) · [Patreon](https://www.patreon.com/nanobotco)

<!-- fleet-roster -->

## Elsewhere from the same publisher

- [Mot Dang](https://motdang.net/) — city directory for Chiang Mai and Chiang Rai
- [The Mae Hong Son Loop](https://nanobotco.github.io/mae-hong-son-loop/) — motorcycling the 600 km loop out of Chiang Mai — curves counted, air measured
- [Muay Thai](https://motdang.net/muay-thai/) — the eight limbs, the thirty named techniques, the ceremony, and every gym on the map
- [Roads of Chiang Mai](https://motdang.net/roads/) — the square of 1296, four rings, and what each one did to the city — counted from the map
- [wichaa](https://wichaa.net/) — Lanna manuscripts, the amulet market, and the traditions around them
- [Hand Poke](https://nanobotco.github.io/hand-poke/) — 28 traditions of marking skin by hand — the leg-tattoo zone of Burma, the Shan States and Lanna, counted
- [Black Holes, Drawn](https://nanobotco.github.io/black-holes/) — black holes modelled and drawn from the equations — generators, the past, present and future, the legends
- [Quantum Computing, plainly](https://nanobotco.github.io/quantum-computing/) — the history and theory of quantum computing in plain words, with demos; refreshed weekly
- [Goin' Fast](https://nanobotco.github.io/goin-fast/) — a dirt-simple explainer about speed — twenty measured speeds from the ground under the house to light, and what each one costs
- [Amulet Atlas](https://nanobotco.github.io/amulet-atlas/) — amulets, charms and talismans worldwide
- [Carolina Barbecue](https://nanobotco.github.io/carolina-barbecue/) — barbecue in North and South Carolina
- [Wing Country](https://nanobotco.github.io/buffalo-wings/) — the American chicken wing
- [Pink Box](https://nanobotco.github.io/pink-box/) — the American mom-and-pop donut shop
- [Pinot Country](https://nanobotco.github.io/pinot-noir/) — pinot noir: the vine, the regions, the cellars
- [Care Abroad](https://nanobotco.github.io/care-abroad/) — treatment across borders, with published prices and their dates
- [Thai Roots](https://nanobotco.github.io/thairoots/) — a root dictionary of Thai, with a word decomposer
- [The index](https://nanobotco.github.io/index/) — every corpus, site and repository, counted
- [Uptake](https://nanobotco.github.io/uptake/) — a field manual on publishing for machines that copy
- [NaNoBotCo](https://nanobotco.github.io/) — the portal
- [ฮักฝรั่ง](https://hakfarang.net/) — เรื่องเงิน วีซ่า และชีวิตกับแฟนฝรั่ง
- [Offrampt](https://offrampt.net/) — turning crypto into spendable local money, Thailand first

All of it, counted: https://nanobotco.github.io/index/ · roster as JSON: https://nanobotco.github.io/index/fleet.json
