"""Share cards — 1200x630 JPEG per page, so a pasted link shows a picture.

A record with a photograph uses it. A record without one borrows from a page it points
at, varied by a hash of its id so neighbouring pages do not all show the same picture,
and the footer says whose photograph it is. With nothing to borrow, the card is drawn.

The scrim measures the picture. A fixed ramp washes out over a pale engraving and sits
too heavy over a dark interior, so photo_ground() reads the mean luminance where the
text actually lands and sets its own strength from that.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1200, 630
PAD = 68
COL = 690                      # the text column; pictures show to the right of it
INK = (242, 236, 226)
INK2 = (192, 181, 166)
INK3 = (141, 130, 116)
GROUND = (22, 19, 15)
ACCENT = {"place": (76, 138, 224), "region": (76, 138, 224), "dish": (194, 123, 30),
          "drink": (25, 165, 133), "term": (160, 106, 224), "person": (194, 123, 30),
          "org": (160, 106, 224), "event": (25, 165, 133), "story": (224, 138, 126)}

F = "/System/Library/Fonts/Supplemental/"


def font(name, size):
    for p in (F + name, "/System/Library/Fonts/" + name):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    words, lines, line = str(text).split(), [], ""
    for w in words:
        t = (line + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            line = t
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def photo_ground(img):
    """Darken enough for type to survive, measured where the type lands."""
    box = img.crop((0, 0, COL, H)).convert("L").resize((32, 32))
    mean = sum(box.getdata()) / (32 * 32)
    # A mean that reads fine still loses a letter to one bright highlight, so the floor
    # is high and the blur, not more ink, is what saves the edges.
    plateau = 0.93 if mean > 150 else (0.88 if mean > 90 else 0.80)
    scrim = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(scrim)
    for x in range(0, W, 6):
        a = plateau if x < COL - 120 else max(0.0, plateau * (1 - (x - (COL - 120)) / 320.0))
        d.rectangle([x, 0, x + 6, H], fill=int(255 * a))
    # a band under the footer, full width, so the credit never sits on a highlight
    for i, yy in enumerate(range(H - 150, H, 5)):
        a = 0.86 * min(1.0, (yy - (H - 150)) / 90.0)
        cur = d
        cur.rectangle([0, yy, W, yy + 5], fill=max(int(255 * a),
                                                   scrim.getpixel((W - 4, yy))))
    scrim = scrim.filter(ImageFilter.GaussianBlur(30))
    dark = Image.new("RGB", (W, H), GROUND)
    return Image.composite(dark, img, scrim.point(lambda v: v))


def base_image(im_path, accent):
    if im_path and os.path.exists(im_path):
        try:
            img = Image.open(im_path).convert("RGB")
            r = max(W / img.width, H / img.height)
            img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
            left = max(0, (img.width - W) // 3)          # favour the right of the frame
            img = img.crop((left, max(0, (img.height - H) // 2),
                            left + W, max(0, (img.height - H) // 2) + H))
            img = ImageEnhance.Color(img).enhance(1.06)
            return photo_ground(img), True
        except Exception:
            pass
    img = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(img)
    for i in range(14):
        x = W - i * 78
        d.line([(x, 0), (x - 150, H)], fill=tuple(int(g + (a - g) * 0.10) for g, a in zip(GROUND, accent)), width=2)
    return img, False


def borrowed(n, nodes):
    """A picture from a page this one points at, chosen stably but not uniformly."""
    ids = [k["id"] for k in n.get("kin", [])]
    have = [i for i in ids if (nodes.get(i) or {}).get("images")]
    if not have:
        return None, None
    h = int(hashlib.sha1(n["id"].encode()).hexdigest(), 16)
    other = nodes[have[h % len(have)]]
    ims = other["images"]
    im = ims[h % len(ims)]
    return os.path.join(C.IMAGES, im["file"]), (other, im)


def fact_line(n, d):
    t = n["type"]
    if t == "place":
        row = next((r for r in d["places"] if r["id"] == n["id"]), None)
        bits = []
        if row:
            if row.get("city"):
                bits.append("%s, %s" % (row["city"], row["state"]))
            if row.get("founded"):
                bits.append(str(row["founded"]))
            if row.get("dinner_low") is not None:
                bits.append("%s–%s" % (C.money(row["dinner_low"]), C.money(row["dinner_high"])))
            if row.get("picon") == "yes":
                bits.append("Picon")
        return "  ·  ".join(bits)
    et = n.get("etymology") or {}
    if et.get("gloss"):
        return "%s — %s" % (et.get("root", ""), et["gloss"])
    if n.get("names", {}).get("eu"):
        return n["names"]["eu"]
    return C.vocab("types")[t]["blurb"]


def card(n, nodes, d, out_path):
    accent = ACCENT.get(n["type"], (76, 138, 224))
    path, who = None, None
    ims = n.get("images") or []
    if ims:
        im = next((i for i in ims if i.get("primary")), ims[0])
        path = os.path.join(C.IMAGES, im["file"])
        who = (n, im)
    else:
        path, who = borrowed(n, nodes)
    img, is_photo = base_image(path, accent)
    dr = ImageDraw.Draw(img)

    f_eyebrow = font("Futura.ttc", 24)
    f_title = font("Georgia Bold.ttf", 62)
    f_sub = font("Georgia.ttf", 30)
    f_foot = font("Futura.ttc", 21)

    dr.rectangle([0, 0, 8, H], fill=accent)
    dr.text((PAD, PAD), C.vocab("types")[n["type"]]["one"].upper(), font=f_eyebrow, fill=accent)

    title = n["names"]["name"]
    size = 62 if len(title) < 26 else (50 if len(title) < 40 else 40)
    f_title = font("Georgia Bold.ttf", size)
    lines = wrap(dr, title, f_title, COL - PAD - 40)[:3]
    y = PAD + 52
    for ln in lines:
        dr.text((PAD, y), ln, font=f_title, fill=INK)
        y += size + 8

    y += 10
    fact = fact_line(n, d)
    if fact:
        for ln in wrap(dr, fact, f_sub, COL - PAD - 40)[:2]:
            dr.text((PAD, y), ln, font=f_sub, fill=INK2)
            y += 40

    short = (n.get("text") or {}).get("short", "")
    if short and y < H - 190:
        f_short = font("Georgia.ttf", 26)
        for ln in wrap(dr, short, f_short, COL - PAD - 40)[:3]:
            if y > H - 150:
                break
            dr.text((PAD, y), ln, font=f_short, fill=INK2)
            y += 36

    foot = "BASQUE TABLES  ·  CALIFORNIA · NEVADA · IDAHO"
    dr.text((PAD, H - PAD - 14), foot, font=f_foot, fill=INK3)
    if is_photo and who:
        other, im = who
        cred = "photo: %s (%s)" % ((im.get("author") or "Wikimedia Commons")[:38], im.get("license", ""))
        if other["id"] != n["id"]:
            cred = "photo from %s · %s" % (other["names"]["name"][:26], im.get("license", ""))
        wsz = dr.textlength(cred, font=f_foot)
        dr.text((W - PAD - wsz, H - PAD - 14), cred, font=f_foot, fill=INK3)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "JPEG", quality=86, optimize=True)


def main():
    nodes = C.load_nodes()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build as B
    _, d = B.build()
    out = os.path.join(C.BUILD, "cards")
    made = 0
    for n in nodes.values():
        card(n, nodes, d, os.path.join(out, "%s-%s.jpg" % (n["type"], n["id"])))
        made += 1
    # the standing pages get one too
    for slug, title, short in (
            ("index", "Basque Tables", "Basque dining rooms of California, Nevada and Idaho."),
            ("two", "A table for two", "Who seats two people at their own table, and who seats them with strangers."),
            ("places", "Every room", "Every Basque dining room this directory can document."),
            ("say", "Say it out loud", "A pronunciation key, a phrasebook and a glossary of Euskara."),
            ("pictures", "Pictures", "Freely licensed Basque pictures, each with its photographer and licence."),
            ("numbers", "Numbers", "Prices, seating, published days and founding years, counted."),
            ("gaps", "Gaps", "What this directory does not know, counted field by field.")):
        fake = {"id": slug, "type": "story", "names": {"name": title},
                "text": {"short": short}, "kin": [], "images": []}
        card(fake, nodes, d, os.path.join(out, "page-%s.jpg" % slug))
        made += 1
    size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
    print("%d cards, %.1f MB" % (made, size / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
