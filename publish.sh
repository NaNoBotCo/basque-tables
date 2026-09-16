#!/bin/sh
# validate → test → build → site → copy into docs/ for GitHub Pages.
# When a domain is bought:  CNAME=example.com ./publish.sh
set -e
cd "$(dirname "$0")"
if [ -n "$CNAME" ]; then echo "$CNAME" > docs/CNAME 2>/dev/null || { mkdir -p docs; echo "$CNAME" > docs/CNAME; }; fi
HOST=""
[ -f docs/CNAME ] && HOST="https://$(cat docs/CNAME)"
[ -z "$HOST" ] && HOST="https://nanobotco.github.io/basque-tables"
export SITE_URL="$HOST"
echo "publishing for $SITE_URL"
python3 tools/validate.py
python3 tools/site.py
python3 tools/cards.py
python3 tests/test_all.py
[ -f docs/CNAME ] && cp docs/CNAME /tmp/_bt_cname || true
rm -rf docs
cp -R build docs
touch docs/.nojekyll
[ -f /tmp/_bt_cname ] && cp /tmp/_bt_cname docs/CNAME || true
grep -q "$SITE_URL" docs/sitemap.xml || { echo "host gate FAILED: sitemap does not carry $SITE_URL"; exit 3; }
echo "docs/ ready — $(find docs -name index.html | wc -l | tr -d ' ') pages"
