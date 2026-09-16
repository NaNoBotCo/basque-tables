"""Paths, loading, and the small helpers every tool shares. Standard library only."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
NODES = os.path.join(DATA, "nodes")
VOCAB = os.path.join(DATA, "vocab")
SCHEMA = os.path.join(ROOT, "schema", "node.schema.json")
BUILD = os.path.join(ROOT, "build")
DOCS = os.path.join(ROOT, "docs")

SITE_URL = os.environ.get("SITE_URL", "https://nanobotco.github.io/basque-tables")
SITE_NAME = "Basque Tables"
BYLINE = "NaN"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def vocab(name):
    return load_json(os.path.join(VOCAB, name + ".json"))


def sources():
    return load_json(os.path.join(DATA, "sources", "sources.json"))


def node_paths():
    out = []
    for kind in sorted(os.listdir(NODES)):
        d = os.path.join(NODES, kind)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".json"):
                out.append(os.path.join(d, fn))
    return out


def load_nodes():
    nodes = {}
    for p in node_paths():
        n = load_json(p)
        n["_path"] = p
        nodes[n["id"]] = n
    return nodes


def by_type(nodes, kind):
    return sorted((n for n in nodes.values() if n["type"] == kind), key=sort_key)


def sort_key(n):
    names = n.get("names", {})
    return (names.get("sort") or names.get("name") or n["id"]).lower()


def money(v):
    if v is None:
        return ""
    return ("$%d" % v) if float(v) == int(v) else ("$%.2f" % v)


def state_of(n):
    return (n.get("address") or {}).get("state")


def open_days(n):
    h = n.get("hours") or {}
    return set(h.get("open") or [])


def closed_days(n):
    h = n.get("hours") or {}
    return set(h.get("closed") or [])


def unpublished_days(n):
    if not n.get("hours"):
        return set(DAYS)
    return set(DAYS) - open_days(n) - closed_days(n)


QUOTED = re.compile(r"[“\"'‘]([^”\"'’]{2,400})[”\"'’]")


def unquoted(text):
    """Drop quoted spans so a source's own word is not held against our prose."""
    return QUOTED.sub(" ", text or "")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return s or "x"


IMAGES = os.path.join(DATA, "images")


def jdump(obj, path):
    os.makedirs(os.path.dirname(str(path)), exist_ok=True)
    with open(str(path), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def jload(path):
    return load_json(str(path))


def node_list():
    return list(load_nodes().values())
