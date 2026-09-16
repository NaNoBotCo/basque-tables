#!/bin/sh
cd "$(dirname "$0")"
while true; do
  printf '\n\n  BASQUE TABLES\n'
  printf '  ─────────────────────────────\n'
  printf '   1   Check the records\n'
  printf '   2   Build the site\n'
  printf '   3   Look at it in a browser\n'
  printf '   4   Run the tests\n'
  printf '   5   Publish to docs/\n'
  printf '   6   Read me\n'
  printf '   7   How to write a record\n'
  printf '   0   Quit\n\n'
  printf '  Press a number: '
  read n
  case "$n" in
    1) python3 tools/validate.py; printf '\n  Press return '; read x ;;
    2) python3 tools/site.py; printf '\n  Press return '; read x ;;
    3) (sleep 2; open http://localhost:8802/) & python3 tools/serve.py ;;
    4) python3 tests/test_all.py; printf '\n  Press return '; read x ;;
    5) ./publish.sh; printf '\n  Press return '; read x ;;
    6) less README.txt ;;
    7) less AUTHORING.txt ;;
    0) exit 0 ;;
  esac
done
