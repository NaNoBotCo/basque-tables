BASQUE TABLES
Basque dining rooms of California, Nevada and Idaho — a directory that names its sources.

WHAT IT IS
  One JSON record per node — a room, a dish, a drink, a word, a person, an organization,
  an event, a story, a state. Static HTML built from those records by four scripts. No
  framework, no database, no webfont, no CDN, no tracking. Python 3 standard library only.

  The question it is built to answer: two people want dinner. Will the house seat them at
  their own table or at a long table with strangers, what does it cost, which nights is it
  open, and does the bar make a Picon Punch. Every one of those is a field with a source.

THE BASE PATH — read this before changing a link
  The site is published at a PATH (/basque-tables/), not a host root, because a GitHub
  project page is served that way. So a link written "/places/" would land on the user
  site and 404. common.BASE is taken from SITE_URL's own path and stamped onto every
  internal href and src when the page is written; serve.py mounts the build under the
  same base so local matches live; and a test refuses to publish if anything is missing
  it. Buy a domain and BASE becomes "" and none of this does anything.

THE RULE THAT SHAPES EVERYTHING
  Three states, never two. A day in hours.open is open. A day in hours.closed is closed. A
  day in neither is NOT PUBLISHED, and it is excluded from every filter rather than guessed
  either way. Same for seating and for the Picon: unknown is a value, not a blank.

  And: seating, picon, prices, hours, status and address may never rest on tier "tradition"
  or "inference". The validator refuses it. A reader drives on those fields.

RUN IT
  python3 tools/validate.py     refuse anything the site should not publish
  python3 tools/build.py        counts, kin backlinks, price and hours tables, search docs
  python3 tools/site.py         write build/ — English at /, Euskara at /eu/
  python3 tools/serve.py        look at it on http://localhost:8802/basque-tables/
  python3 tests/test_all.py     run before any publish
  ./publish.sh                  validate, build, site, copy into docs/ for GitHub Pages

  Or double-click "Basque Tables.command" for a numbered menu.

PICTURES
  python3 tools/harvest_commons.py --search "Cyrus Jacobs Uberuaga"
  python3 tools/harvest_commons.py --walk "Category:Lauburu" --depth 2
      Both write a triage list to data/images/_triage/ and download nothing.
  python3 tools/assign_images.py
      The picks, by hand, record by record. Edit PICKS at the top.
  python3 tools/harvest_commons.py --harvest --apply
      Download what is assigned. Only CC0, public domain, CC BY, CC BY-SA and FAL pass;
      anything else is named and skipped. Each file gets a .json sidecar with the
      photographer, the licence and a sha256, and the credit is printed on every page.

EUSKARA
  /say/ is the pronunciation key, a 28-phrase phrasebook and the glossary. The data is
  data/vocab/pronounce.json and data/vocab/phrases.json, both written by this project
  and NOT reviewed by a Basque speaker — the English sits beside the Basque so a speaker
  can correct it without reading code. One phrase is dealt to every record page as a
  callout, picked from the record's own id so it is stable, and from a group that suits
  the page (a bar toast on a drink, a greeting on a room).

  data/vocab/eu.json is the interface, English beside Basque, with `check: true` on the
  strings a Basque speaker should look at first. The record write-ups are NOT translated.
  No English-to-Basque machine translator was available: Cloudflare Workers AI's
  m2m100-1.2b rejects "eu" outright (verified 2026-09-16), and nothing local is installed.
  A Basque speaker, or an API that covers Euskara, closes this.

LAYOUT
  data/nodes/<type>/<id>.json   the records
  data/sources/sources.json     every source id a record may cite; the validator refuses others
  data/vocab/                   types, regions, tiers, banned words, the Euskara interface,
                                the pronunciation key and the phrasebook
  data/geo/towns.json           town centroids — not doorways — for the map and distances
  data/images/                  downloaded pictures, each with a .json sidecar
  schema/node.schema.json       the record shape
  tools/                        common, validate, build, site, pages, viz, harvest, serve
  build/                        the rendered site (throwaway)
  docs/                         the published build

READ NEXT
  AUTHORING.txt — how to write a record, what each tier means, and the house style.


LICENCE
Records, prose and pages: CC BY 4.0. Other layers — upstream data,
pictures, tools — keep their own terms, set out in LICENSE.

USING IT
Attribution is the whole of the condition — copy it, adapt it, sell it,
index it, train on it, and say where it came from. Open an issue if
something is missing:
https://github.com/NaNoBotCo/basque-tables/issues

---

Contact: Nan · nan@motdang.net · Sponsor: ko-fi.com/defiantchiangmai · patreon.com/nanobotco

<!-- fleet-roster -->

Elsewhere from the same publisher

- Mot Dang — https://motdang.net/ — city directory for Chiang Mai and Chiang Rai
- wichaa — https://wichaa.net/ — Lanna manuscripts, the amulet market, and the traditions around them
- Amulet Atlas — https://nanobotco.github.io/amulet-atlas/ — amulets, charms and talismans worldwide
- Carolina Barbecue — https://nanobotco.github.io/carolina-barbecue/ — barbecue in North and South Carolina
- Wing Country — https://nanobotco.github.io/buffalo-wings/ — the American chicken wing
- Pink Box — https://nanobotco.github.io/pink-box/ — the American mom-and-pop donut shop
- Pinot Country — https://nanobotco.github.io/pinot-noir/ — pinot noir: the vine, the regions, the cellars
- Care Abroad — https://nanobotco.github.io/care-abroad/ — treatment across borders, with published prices and their dates
- Thai Roots — https://nanobotco.github.io/thairoots/ — a root dictionary of Thai, with a word decomposer
- The index — https://nanobotco.github.io/index/ — every corpus, site and repository, counted
- Uptake — https://nanobotco.github.io/uptake/ — a field manual on publishing for machines that copy
- NaNoBotCo — https://nanobotco.github.io/ — the portal
- ฮักฝรั่ง — https://hakfarang.net/ — เรื่องเงิน วีซ่า และชีวิตกับแฟนฝรั่ง
- Offrampt — https://offrampt.net/ — turning crypto into spendable local money, Thailand first

All of it, counted: https://nanobotco.github.io/index/ · roster as JSON: https://nanobotco.github.io/index/fleet.json
