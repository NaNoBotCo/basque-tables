"""Refuse anything the site should not publish. Standard library only.

Runs a subset of JSON Schema against schema/node.schema.json, then the rules that
matter more than the shape: sources must be registered, a fact a reader drives on
may not rest on tradition or inference, a day may not be both open and closed, and
our own prose may not carry the banned words.
"""
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import common as C


def check_schema(node, schema, path="", errs=None, root=None):
    errs = errs if errs is not None else []
    root = root or schema
    if "$ref" in schema:
        return errs
    t = schema.get("type")
    if t:
        ok = {
            "object": dict, "array": list, "string": str,
            "number": (int, float), "integer": int, "boolean": bool,
        }[t]
        if t == "integer" and isinstance(node, bool):
            errs.append("%s: expected integer" % path)
            return errs
        if not isinstance(node, ok):
            errs.append("%s: expected %s, got %s" % (path or "/", t, type(node).__name__))
            return errs
    if "const" in schema and node != schema["const"]:
        errs.append("%s: must equal %r" % (path, schema["const"]))
    if "enum" in schema and node not in schema["enum"]:
        errs.append("%s: %r not one of %s" % (path, node, schema["enum"]))
    if isinstance(node, str):
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errs.append("%s: %r fails pattern %s" % (path, node, schema["pattern"]))
        if "minLength" in schema and len(node) < schema["minLength"]:
            errs.append("%s: shorter than %d" % (path, schema["minLength"]))
        if "maxLength" in schema and len(node) > schema["maxLength"]:
            errs.append("%s: longer than %d (is %d)" % (path, schema["maxLength"], len(node)))
    if isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            errs.append("%s: needs at least %d" % (path, schema["minItems"]))
        if "items" in schema:
            for i, v in enumerate(node):
                check_schema(v, schema["items"], "%s[%d]" % (path, i), errs, root)
    if isinstance(node, dict):
        for k in schema.get("required", []):
            if k not in node:
                errs.append("%s: missing %s" % (path or "/", k))
        props = schema.get("properties", {})
        pats = schema.get("patternProperties", {})
        for k, v in node.items():
            if k.startswith("_"):
                continue
            if k in props:
                check_schema(v, props[k], "%s/%s" % (path, k), errs, root)
            elif any(re.search(p, k) for p in pats):
                continue
            elif schema.get("additionalProperties") is False:
                errs.append("%s: unknown key %s" % (path or "/", k))
    return errs


def map_gate():
    """Each room's coordinate against its state's box, and each map's pins against its
    own frame."""
    import basemap
    import build as B
    import viz
    rows = B.build()[1]["places"]
    pts = [("place/" + r["id"], r["lat"], r["lon"], r["state"]) for r in rows if r.get("lat")]
    frames = []
    fr = viz.scatter_frame(rows)
    if fr:
        frames.append(("home map", fr, [(r["lat"], r["lon"]) for r in rows if r.get("lat")]))
    for r in rows:
        fr, _, pins = viz.locator_layout(r, rows)
        if fr:
            frames.append(("place/" + r["id"], fr, [(la, lo) for *_, la, lo in pins]))
    return basemap.gate(pts, frames)


DRIVEN_ON = ["seating", "picon", "prices", "hours", "status", "address"]
SOFT_TIERS = {"tradition", "inference"}


def main():
    nodes = C.load_nodes()
    schema = C.load_json(C.SCHEMA)
    registry = C.sources()
    banned = C.vocab("banned")
    regions = C.vocab("regions")
    types = C.vocab("types")
    errs = []
    warns = []

    if not nodes:
        errs.append("no records at all")

    for nid, n in sorted(nodes.items()):
        p = n["_path"]
        want = p.rsplit("/", 1)[1][:-5]
        if want != nid:
            errs.append("%s: id %r does not match filename" % (p, nid))
        if "/%s/" % n.get("type", "") not in p:
            errs.append("%s: sits in the wrong type folder" % nid)
        for e in check_schema({k: v for k, v in n.items() if k != "_path"}, schema):
            errs.append("%s%s" % (nid, e))

        for s in n.get("sources", []):
            if s not in registry:
                errs.append("%s: source %r is not in data/sources/sources.json" % (nid, s))
        for r in n.get("region", []):
            if r not in regions:
                errs.append("%s: region %r is not in data/vocab/regions.json" % (nid, r))
        if n.get("type") not in types:
            errs.append("%s: type %r is not in data/vocab/types.json" % (nid, n.get("type")))

        for field in DRIVEN_ON:
            blk = n.get(field)
            if isinstance(blk, dict) and blk.get("tier") in SOFT_TIERS:
                errs.append("%s: %s may not rest on tier %r — a reader drives on it"
                            % (nid, field, blk["tier"]))

        h = n.get("hours") or {}
        both = set(h.get("open") or []) & set(h.get("closed") or [])
        if both:
            errs.append("%s: %s is listed both open and closed" % (nid, ", ".join(sorted(both))))

        pr = n.get("prices") or {}
        lo, hi = pr.get("dinner_low"), pr.get("dinner_high")
        if lo is not None and hi is not None and lo > hi:
            errs.append("%s: dinner_low is above dinner_high" % nid)

        for k in n.get("kin", []):
            if k["id"] not in nodes:
                errs.append("%s: kin points at %r, which has no record" % (nid, k["id"]))

        prose = []
        for v in (n.get("text") or {}).values():
            prose.append(v)
        for s in n.get("sections", []):
            prose.append(s.get("body", ""))
            prose.append(s.get("heading", ""))
        blob = C.unquoted(" \n ".join(prose)).lower()
        for word in banned["fluff"] + banned["adjudicating"]:
            if re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(word), blob):
                errs.append("%s: banned word %r in our own prose" % (nid, word))

        if n.get("type") == "place":
            if not n.get("seating"):
                warns.append("%s: no seating recorded — the table-for-two page cannot use it" % nid)
            if not n.get("hours"):
                warns.append("%s: no hours recorded" % nid)
            if not n.get("address", {}).get("state"):
                errs.append("%s: a room needs a state" % nid)

    errs += map_gate()
    print("%d records" % len(nodes))
    for w in warns:
        print("  warn  %s" % w)
    if errs:
        for e in errs:
            print("  ERROR %s" % e)
        print("%d errors" % len(errs))
        return 1
    print("0 errors, %d warnings" % len(warns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
