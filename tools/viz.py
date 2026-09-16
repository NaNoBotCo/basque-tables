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


def scatter_map(rows, towns, width=760):
    """Longitude and latitude, plotted straight. No borders drawn, because we have none
    to draw from — the dots are the towns, and the empty middle is the finding."""
    pts = [r for r in rows if r.get("lat")]
    if not pts:
        return ""
    lons = [r["lon"] for r in pts]
    lats = [r["lat"] for r in pts]
    lo_x, hi_x = min(lons) - 3.5, max(lons) + 3.5
    lo_y, hi_y = min(lats) - 2.2, max(lats) + 2.2
    height = 420
    pad = 40

    def X(lon):
        return pad + (width - 2 * pad) * (lon - lo_x) / (hi_x - lo_x)

    def Y(lat):
        return height - pad - 26 - (height - 2 * pad - 62) * (lat - lo_y) / (hi_y - lo_y)

    out = ['<svg viewBox="0 0 %d %d" role="img" class="chart map" '
           'aria-label="Every room in this directory plotted by longitude and latitude">' % (width, height)]
    out.append(_t(0, 18, "Every room, by longitude and latitude", "ttl"))
    for lon in range(int(lo_x) - 1, int(hi_x) + 2, 5):
        if lo_x <= lon <= hi_x:
            out.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="grid"/>' % (X(lon), pad, X(lon), height - pad))
            out.append(_t(X(lon), height - pad + 16, "%d°W" % abs(lon), "cap", "middle"))
    for lat in range(int(lo_y) - 1, int(hi_y) + 2, 3):
        if lo_y <= lat <= hi_y:
            out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" class="grid"/>' % (pad, Y(lat), width - pad, Y(lat)))
            out.append(_t(pad - 6, Y(lat) + 4, "%d°N" % lat, "cap", "end"))
    grouped = {}
    for r in pts:
        grouped.setdefault(r["town"], []).append(r)
    placed = []
    items = sorted(grouped.items(), key=lambda kv: (Y(kv[1][0]["lat"]), X(kv[1][0]["lon"])))
    for town, rs in items:
        r = rs[0]
        x, y = X(r["lon"]), Y(r["lat"])
        n = len(rs)
        rad = 4.5 + 3.0 * math.sqrt(n)
        fill = {"CA": CAT[0], "NV": CAT[2], "ID": CAT[1]}.get(r["state"], CAT[3])
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.8" '
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
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--rule)" stroke-width="1"/>'
                       % (x + (rad + 2 if right else -rad - 2), y, lx - (2 if right else -2), ly - 4))
        out.append(_t(lx, ly, label, "lab", "start" if right else "end"))
    ly = height - 12
    for i, (st, lab) in enumerate((("CA", "California"), ("NV", "Nevada"), ("ID", "Idaho"))):
        lx = 120 * i
        out.append('<circle cx="%d" cy="%d" r="6" fill="%s"/>' % (lx + 6, ly - 4, {"CA": CAT[0], "NV": CAT[2], "ID": CAT[1]}[st]))
        out.append(_t(lx + 18, ly, lab, "lab"))
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


def locator_svg(row, rows, haversine, width=760, height=300):
    """The room's own state, its towns plotted, this one lit. Honest geography:
    real coordinates, no invented borders, and the nearest neighbour measured."""
    mine = [r for r in rows if r["state"] == row["state"] and r.get("lat")]
    if not row.get("lat") or len(mine) < 2:
        return ""
    lats = [r["lat"] for r in mine]
    lons = [r["lon"] for r in mine]
    padx = max(0.8, (max(lons) - min(lons)) * 0.18)
    pady = max(0.6, (max(lats) - min(lats)) * 0.22)
    lo_x, hi_x = min(lons) - padx, max(lons) + padx
    lo_y, hi_y = min(lats) - pady, max(lats) + pady
    L, R, TOP, BOT = 150, width - 30, 54, height - 34

    def X(lon):
        return L + (R - L) * (lon - lo_x) / (hi_x - lo_x or 1)

    def Y(lat):
        return BOT - (BOT - TOP) * (lat - lo_y) / (hi_y - lo_y or 1)

    state = {"CA": "California", "NV": "Nevada", "ID": "Idaho"}.get(row["state"], row["state"])
    others = [r for r in mine if r["town"] != row["town"]]
    near, miles = None, None
    for r in others:
        d = haversine((row["lat"], row["lon"]), (r["lat"], r["lon"]))
        if miles is None or d < miles:
            near, miles = r, d

    out = ['<svg viewBox="0 0 %d %d" role="img" class="chart plate" '
           'aria-label="%s in %s, with the other rooms in the state">'
           % (width, height, C.esc(row["name"]), C.esc(state))]
    out.append(_t(0, 22, "%s · %s" % (row["town"] or "", state), "ttl"))
    for lat in range(int(lo_y), int(hi_y) + 1):
        if lo_y <= lat <= hi_y:
            out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" class="grid"/>' % (L, Y(lat), R, Y(lat)))
    for lon in range(int(lo_x), int(hi_x) + 1):
        if lo_x <= lon <= hi_x:
            out.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="grid"/>' % (X(lon), TOP, X(lon), BOT))
    if near:
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--rule)" '
                   'stroke-width="1.5" stroke-dasharray="4 4"/>'
                   % (X(row["lon"]), Y(row["lat"]), X(near["lon"]), Y(near["lat"])))
    seen = set()
    for r in others:
        if r["town"] in seen:
            continue
        seen.add(r["town"])
        out.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="var(--rule)"><title>%s</title></circle>'
                   % (X(r["lon"]), Y(r["lat"]), C.esc(r["town"] or "")))
    x, y = X(row["lon"]), Y(row["lat"])
    out.append('<circle cx="%.1f" cy="%.1f" r="15" fill="%s" fill-opacity="0.18"/>' % (x, y, CAT[0]))
    out.append('<circle cx="%.1f" cy="%.1f" r="7.5" fill="%s" stroke="var(--paper)" stroke-width="2.5"/>'
               % (x, y, CAT[0]))
    anchor = "end" if x > width * 0.72 else "start"
    out.append(_t(x + (-14 if anchor == "end" else 14), y + 4,
                  (row["town"] or "").split(",")[0], "val", anchor))

    ly = 74
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
    if near and miles:
        facts.append("%d mi to %s" % (round(miles), (near["town"] or "").split(",")[0]))
    for f in facts[:4]:
        out.append(_t(0, ly, f, "lab"))
        ly += 18
    out.append("</svg>")
    return "".join(out)


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
