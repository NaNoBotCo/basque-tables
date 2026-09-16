"""Run me before any publish: python3 tests/test_all.py"""
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "tools"))
import common as C
import validate as V

FAILS = []


def check(name, ok, detail=""):
    print(("  ok   " if ok else "  FAIL ") + name + (" — " + detail if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def main():
    print("tests")
    check("validate.py passes", V.main() == 0)

    nodes = C.load_nodes()
    reg = C.sources()
    check("every source is registered",
          all(s in reg for n in nodes.values() for s in n["sources"]))

    hard = ["seating", "picon", "prices", "hours", "status", "address"]
    bad = [(n["id"], f) for n in nodes.values() for f in hard
           if isinstance(n.get(f), dict) and n[f].get("tier") in ("tradition", "inference")]
    check("no drive-on field rests on tradition or inference", not bad, str(bad))

    overlap = [n["id"] for n in nodes.values()
               if C.open_days(n) & C.closed_days(n)]
    check("no day is both open and closed", not overlap, str(overlap))

    banned = C.vocab("banned")
    hits = []
    for n in nodes.values():
        blob = " ".join(list((n.get("text") or {}).values())
                        + [s["body"] for s in n.get("sections", [])])
        blob = C.unquoted(blob).lower()
        for w in banned["fluff"] + banned["adjudicating"]:
            if re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(w), blob):
                hits.append((n["id"], w))
    check("no banned word in our own prose", not hits, str(hits))

    if not os.path.isdir(C.BUILD):
        check("site is built", False, "run tools/site.py first")
        return finish()

    htmls = glob.glob(os.path.join(C.BUILD, "**", "index.html"), recursive=True) + \
        [os.path.join(C.BUILD, "404.html")]
    check("pages were written", len(htmls) > 60, str(len(htmls)))

    bare = []
    badld = []
    for f in htmls:
        s = open(f, encoding="utf-8").read()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        for b in blocks:
            try:
                o = json.loads(b)
                if "@type" not in o or "@context" not in o:
                    badld.append(f)
            except Exception:
                badld.append(f)
    check("every JSON-LD block parses and is typed", not badld, str(badld[:3]))

    # THE BUG THIS GUARDS: the site is published under /<repo>/ on GitHub Pages, so a
    # link written "/places/" lands on the USER site and 404s. Every internal path must
    # carry BASE. Caught in the wild after publishing; never again silently.
    unbased = {}
    for f in htmls:
        src = open(f, encoding="utf-8").read()
        for path in re.findall(r'(?:href|src)="(/[^"]*)"', src):
            if C.BASE and not (path == C.BASE or path.startswith(C.BASE + "/")):
                unbased.setdefault(path, f)
    check("every internal path carries the base path %r" % (C.BASE or "(none)"),
          not unbased, str(list(unbased.items())[:4]))

    have = set()
    for f in htmls:
        rel = os.path.relpath(f, C.BUILD)
        have.add("/" + os.path.dirname(rel).replace(os.sep, "/") + "/" if os.path.dirname(rel) else "/")
    dead = set()
    for f in htmls:
        s = open(f, encoding="utf-8").read()
        for href in re.findall(r'href=[\'"](/[^\'"#?]*)[\'"]', s):
            href = href[len(C.BASE):] or "/" if C.BASE and href.startswith(C.BASE) else href
            if href.startswith(("/api/", "/llms", "/sitemap", "/robots", "/images/", "/cards/")):
                continue
            if href.rstrip("/").split("/")[-1] in ("place", "dish", "drink", "term", "person",
                                                   "org", "event", "story", "region"):
                continue  # a JavaScript template, not a link: href="/place/'+r.id+'/"
            if href not in have:
                dead.add(href)
    check("every internal link resolves", not dead, str(sorted(dead)[:6]))

    if shutil_which("node"):
        # Most pages share the same tiny script, so check each distinct body once —
        # spawning node per page took minutes.
        bodies = {}
        for f in htmls:
            src = open(f, encoding="utf-8").read()
            for m in re.findall(r"<script>(.*?)</script>", src, re.S):
                bodies.setdefault(m, f)
        broken = []
        for body, f in bodies.items():
            tmp = "/tmp/_bt_check.js"
            open(tmp, "w").write(body)
            if subprocess.run(["node", "--check", tmp], capture_output=True).returncode:
                broken.append(f)
        check("every inline script parses (%d distinct)" % len(bodies), not broken, str(broken[:3]))
    else:
        print("  skip node --check (node not installed)")

    return finish()


def shutil_which(x):
    import shutil
    return shutil.which(x)


def finish():
    if FAILS:
        print("%d failed" % len(FAILS))
        return 1
    print("all pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
