"""Inline SVG figures. No library, no webfont, no off-page request.

Palette validated with the dataviz skill's validate_palette.js against this site's
own surfaces (#faf6ef light, #16130f dark). Re-run it before changing any colour:
  light categorical #2a6fd6 #c2620a #0f8f79 #9333ea
  dark  categorical #4c8ae0 #c27b1e #19a585 #a06ae0
  light status open #0f8f79 closed #c0392b · dark open #19a585 closed #d4544a
The third state — not published — is a dashed outline with no fill, so it reads
without colour at all.
"""
import math
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import common as C
import basemap
import roads

CAT = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)"]


def _t(x, y, s, cls="lab", anchor="start", extra=""):
    return '<text x="%.1f" y="%.1f" class="%s" text-anchor="%s"%s>%s</text>' % (
        x, y, cls, anchor, (" " + extra if extra else ""), C.esc(s))


def figure(svg, caption, label):
    return ('<figure class="fig"><div class="fig-scroll">%s</div>'
            '<figcaption>%s</figcaption></figure>' % (svg, caption)) if caption else svg


def price_ladder(items, width=720):
    """One bar per printed menu price. One series, so no legend — the title names it."""
    if not items:
        return ""
    rowh, pad_l, pad_t = 26, 210, 34
    h = pad_t + rowh * len(items) + 30
    hi = max(i["usd"] for i in items)
    span = width - pad_l - 80
    out = ['<svg viewBox="0 0 %d %d" role="img" aria-label="Menu prices, low to high" class="chart">' % (width, h)]
    out.append(_t(0, 18, "Every dinner price this directory can quote", "ttl"))
    for n, it in enumerate(items):
        y = pad_t + n * rowh
        w = max(3, span * it["usd"] / hi)
        out.append(_t(pad_l - 10, y + 15, it["item"], "lab", "end"))
        out.append('<rect x="%d" y="%.1f" width="%.1f" height="14" rx="4" fill="%s" class="bar">'
                   '<title>%s — %s</title></rect>'
                   % (pad_l, y + 4, w, CAT[0], C.esc(it["item"]), C.money(it["usd"])))
        out.append(_t(pad_l + w + 8, y + 15, C.money(it["usd"]), "val"))
    out.append(_t(pad_l, h - 8, "source: the house's own menu", "cap"))
    out.append("</svg>")
    return "".join(out)


def three_state_bar(counts, title, order, labels, width=720):
    """A stacked bar where the unknown slice is drawn, not dropped."""
    total = sum(counts.get(k, 0) for k in order) or 1
    out = ['<svg viewBox="0 0 %d 128" role="img" aria-label="%s" class="chart">' % (width, C.esc(title))]
    out.append(_t(0, 18, title, "ttl"))
    x = 0.0
    for n, k in enumerate(order):
        v = counts.get(k, 0)
        if not v:
            continue
        w = width * v / total
        unknown = k in ("unknown", "not published")
        if unknown:
            out.append('<rect x="%.1f" y="30" width="%.1f" height="30" rx="4" fill="none" '
                       'stroke="var(--rule)" stroke-width="2" stroke-dasharray="5 4"><title>%s: %d</title></rect>'
                       % (x + 1, max(2, w - 2), C.esc(labels[k]), v))
        else:
            out.append('<rect x="%.1f" y="30" width="%.1f" height="30" rx="4" fill="%s"><title>%s: %d</title></rect>'
                       % (x + 1, max(2, w - 2), CAT[n % 4], C.esc(labels[k]), v))
        x += w
    x = 0.0
    lx, ly = 0, 86
    for n, k in enumerate(order):
        v = counts.get(k, 0)
        if not v:
            continue
        unknown = k in ("unknown", "not published")
        if unknown:
            out.append('<rect x="%d" y="%d" width="12" height="12" rx="3" fill="none" stroke="var(--rule)" '
                       'stroke-width="2" stroke-dasharray="4 3"/>' % (lx, ly))
        else:
            out.append('<rect x="%d" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (lx, ly, CAT[n % 4]))
        lab = "%s %d" % (labels[k], v)
        out.append(_t(lx + 18, ly + 11, lab, "lab"))
        lx += 26 + 8.4 * len(lab)
        if lx > width - 150:
            lx, ly = 0, ly + 24
    out.append("</svg>")
    return "".join(out)


def week_strip(days, width=720):
    """Seven columns, three states each. The unpublished share is drawn dashed."""
    colw = width / 7.0
    out = ['<svg viewBox="0 0 %d 216" role="img" aria-label="Rooms open by day of week" class="chart">' % width]
    out.append(_t(0, 18, "Which days the houses publish", "ttl"))
    total = max(sum(v.values()) for v in days.values()) or 1
    base, top = 148, 34
    for i, d in enumerate(C.DAYS):
        v = days[d]
        x = i * colw + 8
        w = colw - 16
        y = base
        for key, fill in (("open", "var(--ok)"), ("closed", "var(--no)")):
            hh = (base - top) * v[key] / total
            if hh > 0:
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s">'
                           '<title>%s — %s %d</title></rect>' % (x, y - hh + 1, w, max(2, hh - 2), fill, d, key, v[key]))
            y -= hh
        hh = (base - top) * v["unpublished"] / total
        if hh > 0:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" '
                       'stroke="var(--rule)" stroke-width="2" stroke-dasharray="5 4">'
                       '<title>%s — not published %d</title></rect>' % (x, y - hh + 1, w, max(2, hh - 2), d, v["unpublished"]))
        out.append(_t(x + w / 2, base + 18, d, "lab", "middle"))
        out.append(_t(x + w / 2, base + 36, str(v["open"]), "val", "middle"))
    out.append('<rect x="0" y="192" width="12" height="12" rx="3" fill="var(--ok)"/>')
    out.append(_t(18, 203, "open", "lab"))
    out.append('<rect x="72" y="192" width="12" height="12" rx="3" fill="var(--no)"/>')
    out.append(_t(90, 203, "closed", "lab"))
    out.append('<rect x="156" y="192" width="12" height="12" rx="3" fill="none" stroke="var(--rule)" '
               'stroke-width="2" stroke-dasharray="4 3"/>')
    out.append(_t(174, 203, "not published — kept out of every filter", "lab"))
    out.append("</svg>")
    return "".join(out)


def year_timeline(rows, width=720):
    years = [(r["founded"], r["name"], r["status"]) for r in rows if r.get("founded")]
    if not years:
        return ""
    years.sort()
    lo, hi = years[0][0], years[-1][0]
    span = max(hi - lo, 1)
    left, right = 96, width - 96
    out = ['<svg viewBox="0 0 %d 220" role="img" aria-label="When each room opened" class="chart">' % width]
    out.append(_t(0, 18, "When the doors opened", "ttl"))
    out.append('<line x1="%d" y1="120" x2="%d" y2="120" stroke="var(--rule)" stroke-width="2"/>' % (left, right))
    for decade in range(int(lo // 10 * 10), int(hi // 10 * 10) + 11, 20):
        if decade < lo - 5 or decade > hi + 5:
            continue
        x = left + (right - left) * (decade - lo) / span
        out.append('<line x1="%.1f" y1="114" x2="%.1f" y2="126" stroke="var(--rule)"/>' % (x, x))
        out.append(_t(x, 144, str(decade), "lab", "middle"))
    flip = 0
    for y, name, status in years:
        x = left + (right - left) * (y - lo) / span
        up = -1 if flip % 2 == 0 else 1
        ly = 120 + up * (30 + 22 * (flip % 4 // 2))
        closed = status == "closed"
        out.append('<line x1="%.1f" y1="120" x2="%.1f" y2="%.1f" stroke="var(--rule)"/>' % (x, x, ly))
        out.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="var(--paper)" stroke-width="2">'
                   '<title>%s — %d</title></circle>'
                   % (x, ly, "var(--no)" if closed else CAT[2], C.esc(name), y))
        anchor, lx = "middle", x
        if x < 120:
            anchor, lx = "start", 0
        elif x > width - 120:
            anchor, lx = "end", width
        out.append(_t(lx, ly + (-12 if up < 0 else 20), "%d %s" % (y, name), "lab", anchor))
        flip += 1
    out.append("</svg>")
    return "".join(out)


STATE_FILL = {"CA": CAT[0], "NV": CAT[2], "ID": CAT[1]}
MAP_H = 560


def scatter_frame(rows, width=760):
    """Every room in one frame, equal metres on both axes."""
    pts = [(r["lat"], r["lon"]) for r in rows if r.get("lat")]
    return basemap.Frame.fit(pts, width, MAP_H, pad=0.1) if pts else None


def scatter_map(rows, towns, width=760):
    """Every room over Natural Earth land, water, state lines and highways, one dot per
    town sized by its rooms. Town centroids, not doorways."""
    pts = [r for r in rows if r.get("lat")]
    fr = scatter_frame(rows, width)
    if not fr:
        return ""
    height = fr.h
    grouped = {}
    for r in pts:
        grouped.setdefault(r["town"], []).append(r)
    dots = [(fr.xy(rs[0]["lon"], rs[0]["lat"]), 4.5 + 3.0 * math.sqrt(len(rs))) for rs in grouped.values()]
    out = ['<svg viewBox="0 0 %d %d" role="img" class="chart map bm" style="border-radius:10px;overflow:hidden" '
           'aria-label="Every room in this directory on a map of California, Nevada and Idaho">' % (width, height)]
    out.append(basemap.draw(fr, basemap.load(), [(x, y, r + 4) for (x, y), r in dots], towns=0))
    out.append(_t(12, 24, "Every room, by town", "ttl"))
    placed = [(x - r, x + r, y + 4) for (x, y), r in dots]     # labels keep off every dot
    items = sorted(grouped.items(), key=lambda kv: (fr.xy(kv[1][0]["lon"], kv[1][0]["lat"])[1],
                                                    fr.xy(kv[1][0]["lon"], kv[1][0]["lat"])[0]))
    for town, rs in items:
        r = rs[0]
        x, y = fr.xy(r["lon"], r["lat"])
        n = len(rs)
        rad = 4.5 + 3.0 * math.sqrt(n)
        fill = STATE_FILL.get(r["state"], CAT[3])
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.85" '
                   'stroke="var(--paper)" stroke-width="2" class="dot"><title>%s — %d</title></circle>'
                   % (x, y, rad, fill, C.esc(town), n))
        label = "%s (%d)" % (town.split(",")[0], n)
        w = 6.6 * len(label)
        right = x < width * 0.6
        lx = x + rad + 7 if right else x - rad - 7
        ly = y + 4
        x0, x1 = (lx, lx + w) if right else (lx - w, lx)
        step, tries = 15, 0
        while any(abs(ly - py) < 14 and not (x1 < px0 or x0 > px1) for px0, px1, py in placed) and tries < 24:
            tries += 1
            ly = y + 4 + step * ((tries + 1) // 2) * (1 if tries % 2 else -1)
        placed.append((x0, x1, ly))
        if abs(ly - (y + 4)) > 6:
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--ink3)" stroke-width="1"/>'
                       % (x + (rad + 2 if right else -rad - 2), y, lx - (2 if right else -2), ly - 4))
        out.append(_t(lx, ly, label, "lab halo", "start" if right else "end"))
    ly = 24
    for i, (st, lab) in enumerate((("CA", "California"), ("NV", "Nevada"), ("ID", "Idaho"))):
        lx = width - 330 + 110 * i
        out.append('<circle cx="%d" cy="%d" r="6" fill="%s"/>' % (lx + 6, ly - 4, STATE_FILL[st]))
        out.append(_t(lx + 18, ly, lab, "lab halo"))
    out.append(basemap.scale_bar(fr))
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- drawn heroes
# A record with no photograph still opens on a picture. These are drawn from the
# record's own fields, so they carry information rather than decoration — a room
# gets its own county, a word gets its root, a person gets the rooms they opened.

def _wrap(s, n):
    out, line = [], ""
    for word in str(s).split():
        if len(line) + len(word) + 1 > n:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return out


LOC_W, LOC_H, LOC_L = 760, 300, 250      # the plate, and where its map begins


def locator_layout(row, rows):
    """The frame for a room's map — the room and its nearest neighbouring town, with
    every other room that falls inside — and the pins: (x, y, town, lat, lon), room first."""
    if not row.get("lat"):
        return None, None, []
    others = [r for r in rows if r.get("lat") and r["town"] != row["town"]]
    here = (row["lat"], row["lon"])
    near = min(others, key=lambda r: roads.crow_mi(here, (r["lat"], r["lon"])), default=None)
    pts = [here] + ([(near["lat"], near["lon"])] if near else [])
    fr = basemap.Frame.fit(pts, LOC_W - LOC_L, LOC_H, pad=0.2, min_km=260)
    pins, seen = [(*fr.xy(row["lon"], row["lat"]), row["town"] or "", row["lat"], row["lon"])], {row["town"]}
    for r in others:
        if r["town"] not in seen and fr.inside(r["lon"], r["lat"], 4):
            seen.add(r["town"])
            pins.append((*fr.xy(r["lon"], r["lat"]), r["town"] or "", r["lat"], r["lon"]))
    return fr, near, pins


def distance_text(a, b):
    """'N mi by road' from the OSRM cache, else 'N mi straight-line'."""
    r = roads.road_mi(a, b)
    return "%d mi by road" % round(r) if r is not None else "%d mi straight-line" % round(roads.crow_mi(a, b))


def locator_svg(row, rows, width=LOC_W, height=LOC_H):
    """The room's town and its nearest neighbouring town on a Natural Earth basemap,
    true scale, the other rooms in view pinned. Town centroids, not doorways."""
    fr, near, pins = locator_layout(row, rows)
    if not fr or not near:
        return ""
    state = {"CA": "California", "NV": "Nevada", "ID": "Idaho"}.get(row["state"], row["state"])
    (x, y, *_), rest = pins[0], pins[1:]
    out = ['<svg viewBox="0 0 %d %d" role="img" class="chart plate" '
           'aria-label="%s in %s, on a map with the nearest room in another town">'
           % (width, height, C.esc(row["name"]), C.esc(state))]
    out.append('<svg class="bm" x="%d" y="0" width="%d" height="%d" viewBox="0 0 %d %d" style="border-radius:10px;overflow:hidden">'
               % (LOC_L, fr.w, fr.h, fr.w, fr.h))
    out.append(basemap.draw(fr, basemap.load(), [(x, y, 20)] + [(px, py, 8) for px, py, *_ in rest], towns=5))
    for px, py, town, *_ in rest:
        out.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="var(--paper)" stroke-width="2"><title>%s</title></circle>'
                   % (px, py, "var(--ink2)", C.esc(town)))
        if town == near["town"]:
            anchor = "end" if px > fr.w * 0.7 else "start"
            out.append(_t(px + (-10 if anchor == "end" else 10), py + 4, town.split(",")[0], "val halo", anchor))
    out.append('<circle cx="%.1f" cy="%.1f" r="15" fill="%s" fill-opacity="0.22"/>' % (x, y, CAT[0]))
    out.append('<circle cx="%.1f" cy="%.1f" r="7.5" fill="%s" stroke="var(--paper)" stroke-width="2.5"/>'
               % (x, y, CAT[0]))
    anchor = "end" if x > fr.w * 0.7 else "start"
    out.append(_t(x + (-14 if anchor == "end" else 14), y + 4, (row["town"] or "").split(",")[0], "val halo", anchor))
    out.append(basemap.scale_bar(fr))
    out.append("</svg>")

    out.append(_t(0, 22, "%s · %s" % (row["town"] or "", state), "ttl"))
    ly = 60
    for line in _wrap(row["name"], 18)[:3]:
        out.append(_t(0, ly, line, "big"))
        ly += 26
    ly += 6
    facts = []
    if row.get("founded"):
        facts.append("opened %s" % row["founded"])
    if row.get("dinner_low") is not None:
        facts.append("dinner %s–%s" % (C.money(row["dinner_low"]), C.money(row["dinner_high"])))
    if row.get("open"):
        facts.append("%d days published" % len(row["open"]))
    facts.append("%s to %s" % (distance_text((row["lat"], row["lon"]), (near["lat"], near["lon"])),
                               (near["town"] or "").split(",")[0]))
    for f in facts[:4]:
        out.append(_t(0, ly, f, "lab"))
        ly += 18
    out.append("</svg>")
    return "".join(out)


def basemap_boxes():
    """Every box a map on this site draws, for tools/basemap.py to clip to."""
    import build as B
    _, d = B.build()
    rows = d["places"]
    boxes = [scatter_frame(rows).box]
    for r in rows:
        fr = locator_layout(r, rows)[0]
        if fr:
            boxes.append(fr.box)
    return boxes


def road_points():
    """Every point tools/roads.py measures between: the towns that hold a room."""
    import build as B
    _, d = B.build()
    return [(r["lat"], r["lon"]) for r in d["places"] if r.get("lat")]


def plate_svg(eyebrow, title, sub=None, lines=None, accent=0, width=760, height=250):
    """A typographic hero for a record with no photograph: the name set large over a
    quiet ruled ground, with whatever the record already knows printed beside it."""
    col = CAT[accent % 4]
    out = ['<svg viewBox="0 0 %d %d" role="img" class="chart plate" aria-label="%s">'
           % (width, height, C.esc(title))]
    out.append('<defs><linearGradient id="g%d" x1="0" y1="0" x2="1" y2="1">'
               '<stop offset="0" stop-color="%s" stop-opacity="0.14"/>'
               '<stop offset="1" stop-color="%s" stop-opacity="0.02"/></linearGradient></defs>' % (accent, col, col))
    out.append('<rect x="0" y="0" width="%d" height="%d" rx="14" fill="url(#g%d)"/>' % (width, height, accent))
    for i in range(1, 9):
        out.append('<line x1="%d" y1="0" x2="%d" y2="%d" stroke="%s" stroke-opacity="0.10" stroke-width="1"/>'
                   % (width - i * 42, width - i * 42 - 70, height, col))
    out.append('<rect x="0" y="0" width="5" height="%d" rx="2.5" fill="%s"/>' % (height, col))
    out.append(_t(28, 34, eyebrow, "ttl"))
    size = 46 if len(title) < 16 else (36 if len(title) < 26 else 28)
    ly = 46 + size
    for line in _wrap(title, max(14, int(620 / (size * 0.52))))[:3]:
        out.append('<text x="28" y="%d" class="plate-title" style="font-size:%dpx">%s</text>'
                   % (ly, size, C.esc(line)))
        ly += size + 6
    if sub:
        ly += 4
        out.append(_t(28, ly, sub, "val"))
        ly += 22
    for line in (lines or [])[:3]:
        for seg in _wrap(line, 62)[:2]:
            out.append(_t(28, ly, seg, "lab"))
            ly += 18
        ly += 2
    out.append("</svg>")
    return "".join(out)
