"""Turn the records into the derived layer the site renders from.

Nothing here invents a fact. Every count is a count of records, and every field a
count rests on names its own source in the record it came from.
"""
import json
import math
import os
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import common as C


def haversine(a, b):
    r = 3958.8
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def town_of(n):
    ad = n.get("address") or {}
    if ad.get("city") and ad.get("state"):
        return "%s, %s" % (ad["city"], ad["state"])
    return None


def build():
    nodes = C.load_nodes()
    towns = {k: v for k, v in C.load_json(os.path.join(C.DATA, "geo", "towns.json")).items()
             if not k.startswith("_")}
    types = C.vocab("types")
    out = {}

    # --- kin backlinks: what the neighbour says back
    back = {nid: [] for nid in nodes}
    for nid, n in nodes.items():
        for k in n.get("kin", []):
            back[k["id"]].append({"id": nid, "how": k["how"]})
    out["backlinks"] = back

    # --- the places table
    rows = []
    for n in C.by_type(nodes, "place"):
        ad = n.get("address") or {}
        st = n.get("seating") or {}
        pc = n.get("picon") or {}
        pr = n.get("prices") or {}
        rows.append({
            "id": n["id"],
            "name": n["names"]["name"],
            "sort": C.sort_key(n),
            "city": ad.get("city"), "state": ad.get("state"),
            "town": town_of(n),
            "street": ad.get("street"), "phone": ad.get("phone"), "url": ad.get("url"),
            "lat": towns.get(town_of(n), [None, None])[0],
            "lon": towns.get(town_of(n), [None, None])[1],
            "status": (n.get("status") or {}).get("state", "unknown"),
            "founded": (n.get("founded") or {}).get("year"),
            "seating": st.get("kind", "unknown"),
            "reservations": st.get("reservations", "unknown"),
            "picon": pc.get("served", "unknown"),
            "picon_price": pc.get("price"),
            "dinner_low": pr.get("dinner_low"), "dinner_high": pr.get("dinner_high"),
            "open": sorted(C.open_days(n), key=C.DAYS.index),
            "closed": sorted(C.closed_days(n), key=C.DAYS.index),
            "unpublished": sorted(C.unpublished_days(n), key=C.DAYS.index),
            "hours_text": (n.get("hours") or {}).get("text"),
            "short": (n.get("text") or {}).get("short", ""),
            "kitchen": (n.get("x_kitchen") or {}).get("says"),
            "recognitions": len(n.get("recognitions") or []),
        })
    out["places"] = rows

    # --- counts
    counts = {t: len([n for n in nodes.values() if n["type"] == t]) for t in types}
    by_state = {}
    for r in rows:
        by_state.setdefault(r["state"] or "?", []).append(r["id"])
    out["counts"] = {"records": len(nodes), "by_type": counts,
                     "by_state": {k: len(v) for k, v in sorted(by_state.items())}}

    # --- the seating question, three states never two
    seat = {"shared": 0, "own": 0, "both": 0, "bar": 0, "unknown": 0}
    for r in rows:
        seat[r["seating"]] = seat.get(r["seating"], 0) + 1
    picon = {"yes": 0, "no": 0, "unknown": 0}
    for r in rows:
        picon[r["picon"]] = picon.get(r["picon"], 0) + 1
    day_counts = {d: {"open": 0, "closed": 0, "unpublished": 0} for d in C.DAYS}
    for r in rows:
        for d in r["open"]:
            day_counts[d]["open"] += 1
        for d in r["closed"]:
            day_counts[d]["closed"] += 1
        for d in r["unpublished"]:
            day_counts[d]["unpublished"] += 1
    out["seating"] = seat
    out["picon"] = picon
    out["days"] = day_counts

    # --- price: only rooms that print one
    items = []
    for n in C.by_type(nodes, "place"):
        for it in (n.get("prices") or {}).get("items", []):
            items.append({"place": n["id"], "item": it["item"], "usd": it["usd"]})
    items.sort(key=lambda r: r["usd"])
    priced = [r for r in rows if r["dinner_low"] is not None]
    out["prices"] = {
        "items": items,
        "rooms_with_a_price": len(priced),
        "rooms_without": len(rows) - len(priced),
        "median_item": items[len(items) // 2]["usd"] if items else None,
        "low": items[0]["usd"] if items else None,
        "high": items[-1]["usd"] if items else None,
        "dinner_for_two_low": min((r["dinner_low"] for r in priced), default=None),
        "dinner_for_two_high": max((r["dinner_high"] for r in priced), default=None),
    }

    # --- how far apart, from town centroids: straight-line, and by road where roads.py has it
    import roads
    towns_at = {}
    for r in rows:
        if r["lat"]:
            towns_at.setdefault(r["town"], r)
    tl = list(towns_at.values())
    pairs = [(haversine((a["lat"], a["lon"]), (b["lat"], b["lon"])), a, b)
             for i, a in enumerate(tl) for b in tl[i + 1:]]

    def pair(p):
        if not p:
            return None
        crow, a, b = p
        road = roads.road_mi((a["lat"], a["lon"]), (b["lat"], b["lon"]))
        return {"from": a["town"], "to": b["town"], "straight_mi": round(crow),
                "road_mi": None if road is None else round(road)}
    out["distance"] = {
        "closest_cross_state": pair(min((p for p in pairs if p[1]["state"] != p[2]["state"]),
                                        key=lambda p: p[0], default=None)),
        "widest_pair": pair(max(pairs, key=lambda p: p[0], default=None))}

    # --- founding years
    years = sorted(r["founded"] for r in rows if r["founded"])
    out["years"] = {"list": years, "oldest": years[0] if years else None,
                    "newest": years[-1] if years else None,
                    "rooms_with_a_year": len(years), "rooms_without": len(rows) - len(years)}

    # --- coverage: what is missing, per field, so the gaps page counts rather than claims
    fields = ["hours", "seating", "picon", "prices", "founded", "address"]
    cover = {}
    for f in fields:
        have = 0
        for n in C.by_type(nodes, "place"):
            blk = n.get(f)
            if f == "seating" and (blk or {}).get("kind") in (None, "unknown"):
                continue
            if f == "picon" and (blk or {}).get("served") in (None, "unknown"):
                continue
            if blk:
                have += 1
        cover[f] = {"have": have, "of": len(rows)}
    out["coverage"] = cover
    out["open_questions"] = sorted(
        [{"id": n["id"], "name": n["names"]["name"], "q": q}
         for n in nodes.values() for q in n.get("needs_verification", [])],
        key=lambda r: r["name"])

    # --- search documents
    docs = []
    for n in nodes.values():
        blob = [n["names"]["name"]] + n["names"].get("aliases", [])
        for v in (n.get("text") or {}).values():
            blob.append(v)
        ad = n.get("address") or {}
        blob += [ad.get("city") or "", ad.get("state") or "", (n.get("x_kitchen") or {}).get("says") or ""]
        docs.append({"id": n["id"], "type": n["type"], "name": n["names"]["name"],
                     "town": town_of(n) or "", "text": " ".join(x for x in blob if x)[:1200]})
    out["search"] = sorted(docs, key=lambda d: d["name"].lower())

    out["towns"] = towns
    return nodes, out


def main():
    nodes, derived = build()
    os.makedirs(os.path.join(C.BUILD, "api"), exist_ok=True)
    with open(os.path.join(C.BUILD, "derived.json"), "w", encoding="utf-8") as fh:
        json.dump(derived, fh, indent=1, ensure_ascii=False)
    for name in ("places", "counts", "coverage", "prices", "search", "seating", "days"):
        with open(os.path.join(C.BUILD, "api", name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(derived[name], fh, indent=1, ensure_ascii=False)
    c = derived["counts"]
    print("%d records · %d rooms · %s" % (c["records"], c["by_type"]["place"],
          " · ".join("%s %d" % (k, v) for k, v in c["by_state"].items())))
    print("seating: " + " · ".join("%s %d" % (k, v) for k, v in derived["seating"].items() if v))
    print("picon: " + " · ".join("%s %d" % (k, v) for k, v in derived["picon"].items() if v))
    for k, v in derived["distance"].items():
        if v:
            print("%s: %s to %s, %s mi straight-line, %s mi by road"
                  % (k.replace("_", " "), v["from"], v["to"], v["straight_mi"], v["road_mi"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
