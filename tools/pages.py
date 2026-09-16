"""Every page the site publishes, in English at / and in Euskara at /eu/."""
import json
import os
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import common as C
import viz

LANG = "en"
PREFIX = ""
_EU = None


def t(key):
    """One interface string. The table is data/vocab/eu.json, English beside Basque."""
    global _EU
    if _EU is None:
        _EU = C.vocab("eu")
    row = _EU.get(key)
    if not row:
        return key
    return row.get(LANG) or row["en"]


t_ = None


def set_lang(lang):
    global LANG, PREFIX, SEAT_LABEL, SEAT_SHORT, PICON_LABEL, t_
    t_ = t
    LANG = lang
    PREFIX = "/eu" if lang == "eu" else ""
    SEAT_LABEL = {"shared": t("seat_shared"), "own": t("seat_own"), "both": t("seat_both"),
                  "bar": t("seat_bar"), "unknown": t("not_published")}
    SEAT_SHORT = {"shared": t("seat_shared_s"), "own": t("seat_own_s"), "both": t("seat_both_s"),
                  "bar": t("seat_bar_s"), "unknown": t("not_published")}
    PICON_LABEL = {"yes": t("yes"), "no": t("no"), "unknown": t("not_published")}

TYPE_INDEX = {"place": "/places/", "dish": "/dishes/", "drink": "/drinks/", "term": "/words/",
              "person": "/people/", "org": "/organizations/", "event": "/events/",
              "story": "/stories/", "region": "/regions/"}

SEAT_LABEL = {"shared": "a long table, with strangers", "own": "your own table",
              "both": "both, depending on the night", "bar": "a counter",
              "unknown": "not published"}
SEAT_SHORT = {"shared": "long table", "own": "own table", "both": "both", "bar": "counter",
              "unknown": "unknown"}
PICON_LABEL = {"yes": "yes", "no": "no", "unknown": "not published"}


TYPE_WORD = {"place": "room", "dish": "dish", "drink": "drink", "term": "word",
             "person": "person", "org": "organization", "event": "event",
             "story": "story", "region": "region"}
TYPE_WORD_EU = {"place": "jatetxea", "dish": "platera", "drink": "edaria", "term": "hitza",
                "person": "pertsona", "org": "erakundea", "event": "ekitaldia",
                "story": "istorioa", "region": "estatua"}


def img_src(im):
    return "/images/" + im["file"]


def credit(im):
    bits = []
    who = (im.get("author") or "").strip()
    if who and who.lower() not in ("unknown", "anonymous"):
        bits.append(C.esc(who[:80]))
    lic = (im.get("license") or "").strip()
    if lic:
        lurl = im.get("license_url") or ""
        bits.append(('<a href="%s" rel="license nofollow">%s</a>' % (C.esc(lurl), C.esc(lic)))
                    if lurl else C.esc(lic))
    page = im.get("page_url") or ""
    bits.append('<a href="%s" rel="nofollow">Commons</a>' % C.esc(page) if page else "Commons")
    return " · ".join(bits)


def hero(n):
    ims = n.get("images") or []
    if not ims:
        return ""
    im = next((i for i in ims if i.get("primary")), ims[0])
    return ('<figure class="hero"><img src="%s" alt="%s" loading="eager" decoding="async">'
            '<figcaption>%s<br><span class="cred">%s</span></figcaption></figure>'
            % (C.esc(img_src(im)), C.esc(im.get("alt") or ""), C.esc(im.get("alt") or ""), credit(im)))


def gallery(ims, heading=None):
    if not ims:
        return ""
    out = []
    for im in ims:
        out.append('<figure class="shot"><a href="%s"><img src="%s" alt="%s" loading="lazy" decoding="async"></a>'
                   '<figcaption>%s<br><span class="cred">%s</span></figcaption></figure>'
                   % (C.esc(im.get("page_url") or img_src(im)), C.esc(img_src(im)),
                      C.esc(im.get("alt") or ""), C.esc((im.get("alt") or "")[:160]), credit(im)))
    return ("<h2>%s</h2>" % C.esc(heading) if heading else "") + '<div class="shots">%s</div>' % "".join(out)


def type_word(kind):
    return (TYPE_WORD_EU if LANG == "eu" else TYPE_WORD)[kind]


def url(n):
    return "/%s/%s/" % (n["type"], n["id"])


def tier_tag(blk):
    t = (blk or {}).get("tier")
    return '<span class="tier" data-t="%s">%s</span>' % (t, t) if t else ""


def week(row):
    out = ['<span class="week" role="img" aria-label="%s">' % week_alt(row)]
    for d in C.DAYS:
        cls = "o" if d in row["open"] else ("c" if d in row["closed"] else "u")
        out.append('<i class="%s" title="%s %s">%s</i>' % (
            cls, d, {"o": "open", "c": "closed", "u": "not published"}[cls], d[0]))
    out.append("</span>")
    return "".join(out)


def week_alt(row):
    bits = []
    if row["open"]:
        bits.append("open " + ", ".join(row["open"]))
    if row["closed"]:
        bits.append("closed " + ", ".join(row["closed"]))
    if row["unpublished"]:
        bits.append("not published: " + ", ".join(row["unpublished"]))
    return "; ".join(bits) or "no hours published"


def price_cell(row):
    lo, hi = row["dinner_low"], row["dinner_high"]
    if lo is None:
        return '<span style="color:var(--ink3)">not published</span>'
    return "%s–%s" % (C.money(lo), C.money(hi))


# ---------------------------------------------------------------- front
def featured(nodes, d):
    """One room shown in full on the front, because a directory should show what a
    record actually holds before it shows a list of names."""
    n = nodes.get("ogi-deli-elko")
    if not n:
        return ""
    row = next((r for r in d["places"] if r["id"] == "ogi-deli-elko"), None)
    pr = (n.get("prices") or {}).get("items") or []
    ad = n.get("address") or {}
    se = n.get("seating") or {}
    bits = [
        ("%s, %s" % (ad.get("city"), ad.get("state"))),
        C.esc(se.get("note", "")),
    ]
    price = ("<b>%s</b> %s" % (C.money(pr[0]["usd"]), C.esc(pr[0]["item"]))) if pr else ""
    return ("""<section class="featured">
 <p class="eyebrow">%s</p>
 <h2 style="margin-top:.2rem"><a href="/place/ogi-deli-elko/">Ogi Deli, Elko</a></h2>
 <p class="lede">%s</p>
 <div class="facts" style="grid-template-columns:auto 1fr">
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s<br>%s</dd>
  <dt>%s</dt><dd>%s</dd>
 </div>
 <p><a class="chip" href="/place/ogi-deli-elko/">The whole record &rarr;</a>
 <a class="chip" href="/event/pintxo-pote/">What a pintxo-pote is</a>
 <a class="chip" href="/term/mus/">And what mus is</a></p>
</section>""" % (C.esc(t_("room")), C.esc((n.get("text") or {}).get("short", "")),
                 C.esc(t_("where")), C.esc("%s, %s, %s" % (ad.get("street"), ad.get("city"), ad.get("state"))),
                 C.esc(t_("seating")), C.esc(bits[1]),
                 C.esc(t_("week")), week(row) if row else "",
                 C.esc((n.get("hours") or {}).get("text", "")),
                 C.esc(t_("dinner")), price))


def front(nodes, d, shell, write):
    c = d["counts"]
    by = c["by_type"]
    types = C.vocab("types")

    def col(kind, limit=None):
        items = C.by_type(nodes, kind)
        li = []
        for n in items[:limit] if limit else items:
            extra = ""
            ad = n.get("address") or {}
            if ad.get("city"):
                extra = " <em>%s</em>" % C.esc(ad["city"])
            li.append('<li><a href="%s">%s</a>%s</li>' % (url(n), C.esc(n["names"]["name"]), extra))
        more = ""
        label = t_({"place": "rooms", "dish": "dishes", "drink": "drinks", "term": "words",
                    "person": "people", "org": "orgs", "event": "events", "story": "stories",
                    "region": "regions"}[kind]) if LANG == "eu" else types[kind]["label"]
        if limit and len(items) > limit:
            more = '<li><a href="%s">%s %d &rsaquo;</a></li>' % (TYPE_INDEX[kind], t_("all"), len(items))
        return ('<section><h2>%s (%d)</h2><ul>%s%s</ul></section>'
                % (C.esc(label), len(items), "".join(li), more))

    seat = d["seating"]
    picon = d["picon"]
    lang_note = ('<p class="note" lang="eu">%s<br>%s</p>' % (C.esc(t_("prose_note")), C.esc(t_("unreviewed")))
                 if LANG == "eu" else "")
    body = """
<p class="eyebrow">%s</p>
<h1>%s</h1>
<p class="lede">%s</p>
%s
<p><a class="chip" href="/two/" aria-pressed="false">%s</a>
<a class="chip" href="/story/the-long-table/" aria-pressed="false">%s</a>
<a class="chip" href="/region/idaho/" aria-pressed="false">%s</a></p>
<div class="stat">
 <div><span>%s</span><b class="big">%d</b></div>
 <div><span>%s</span><b class="big">%d</b></div>
 <div><span>%s</span><b class="big">%d</b></div>
 <div><span>%s</span><b class="big">%d</b></div>
</div>
<p class="note">%s</p>
<hr>
%s
<hr>
<div class="dir">%s</div>
<hr>
%s
<figcaption>%s</figcaption>
""" % (C.esc(t_("a_directory")), C.esc(t_("front_h1")), C.esc(t_("front_lede")), lang_note,
       C.esc(t_("find_two")), C.esc(t_("why_long")), C.esc(t_("the_block")),
       C.esc(t_("stat_rooms")), by["place"],
       C.esc(t_("stat_own")), seat.get("own", 0) + seat.get("both", 0),
       C.esc(t_("stat_long")), seat.get("shared", 0),
       C.esc(t_("stat_picon")), picon.get("yes", 0),
       C.esc(t_("front_note") % (seat.get("unknown", 0), by["place"])),
       featured(nodes, d),
       "".join([col("region"), col("place", 8), col("story"), col("dish", 6),
                col("drink"), col("term", 6), col("person"), col("event"), col("org")]),
       viz.scatter_map(d["places"], d["towns"]), C.esc(t_("map_caption")))
    write("/", shell(t_("site_title"), body,
                     "A sourced directory of Basque dining rooms in California, Nevada and Idaho: seating, prices, "
                     "hours and the Picon Punch, with every field naming where it came from.", "/",
                     jsonld=[{"@context": "https://schema.org", "@type": "WebSite",
                              "name": C.SITE_NAME, "url": C.SITE_URL,
                              "description": "Basque dining rooms of California, Nevada and Idaho."}]))


# ---------------------------------------------------------------- places table
def places_page(nodes, d, shell, write):
    rows = sorted(d["places"], key=lambda r: (r["state"] or "", r["city"] or "", r["sort"]))
    out = []
    state = None
    for r in rows:
        if r["state"] != state:
            state = r["state"]
            out.append('<tr><th colspan="7" style="padding-top:1.4rem;font-size:.9rem;color:var(--ink)">%s</th></tr>'
                       % {"CA": "California", "NV": "Nevada", "ID": "Idaho"}.get(state, state))
        out.append("<tr><td><a href='/place/%s/'>%s</a></td><td>%s</td><td>%s</td><td>%s</td>"
                   "<td>%s</td><td>%s</td><td>%s</td></tr>"
                   % (r["id"], C.esc(r["name"]), C.esc(r["city"] or ""),
                      C.esc(SEAT_SHORT[r["seating"]]), price_cell(r),
                      PICON_LABEL[r["picon"]], week(r),
                      r["founded"] or '<span style="color:var(--ink3)">—</span>'))
    body = """
<p class="eyebrow">%s</p><h1>%s</h1>
<p class="lede">%d.</p>
<div class="tbl-scroll"><table>
<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>Picon</th><th>%s</th><th>%s</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="note">A dashed square in the week strip means no source publishes that day either way.
It is never counted as open and never counted as closed.</p>
%s
""" % (t_("rooms"), t_("rooms"), len(rows), t_("room"), t_("town"), t_("seating"), t_("dinner"), t_("week"),
       t_("opened"), "".join(out), viz.week_strip(d["days"]))
    write("/places/", shell("Rooms — every Basque dining room here", body,
                            "Every Basque dining room in this directory, by state, with seating, dinner price, "
                            "Picon Punch and published days.", "/places/"))


# ---------------------------------------------------------------- a table for two
TWO_JS = """
(function(){
 var ROWS = __DATA__;
 var f = {state:'', seat:'', picon:false, today:false, price:false};
 var LAB = __SEATLAB__;
 var DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
 var todayName = DAYS[(new Date().getDay()+6)%7];
 var el = document.getElementById('two-results');
 var count = document.getElementById('two-count');
 document.getElementById('today-name').textContent = todayName;
 function pass(r){
  if(f.state && r.state !== f.state) return false;
  if(f.seat === 'own' && !(r.seating === 'own' || r.seating === 'both')) return false;
  if(f.seat === 'shared' && !(r.seating === 'shared' || r.seating === 'both')) return false;
  if(f.picon && r.picon !== 'yes') return false;
  if(f.today && r.open.indexOf(todayName) < 0) return false;
  if(f.price && r.dinner_low === null) return false;
  return true;
 }
 function weekHtml(r){
  var s = '<span class="week">';
  for(var i=0;i<7;i++){
   var d = DAYS[i];
   var c = r.open.indexOf(d)>=0 ? 'o' : (r.closed.indexOf(d)>=0 ? 'c' : 'u');
   s += '<i class="'+c+'" title="'+d+'">'+d[0]+'</i>';
  }
  return s + '</span>';
 }
 function money(v){ return v === null ? '' : '$' + v; }
 function draw(){
  var hits = ROWS.filter(pass);
  count.textContent = hits.length;
  if(!hits.length){
   el.innerHTML = '<div class="gap">No room in the records answers all of that. Loosen a chip, or read '
     + '<a href="/gaps/">what is missing</a> — the commonest reason a room drops out is that nobody published the field.</div>';
   return;
  }
  var h = '';
  for(var i=0;i<hits.length;i++){
   var r = hits[i];
   h += '<div class="card"><h3><a href="/place/'+r.id+'/">'+r.name+'</a></h3>';
   h += '<p>'+(r.city||'')+', '+(r.state||'')+(r.founded?' &middot; opened '+r.founded:'')+'</p>';
   h += '<p><b>'+LAB[r.seating]+'</b>';
   if(r.picon === 'yes'){ h += ' &middot; Picon' + (r.picon_price ? ' ' + money(r.picon_price) : ''); }
   if(r.dinner_low !== null){ h += ' &middot; dinner ' + money(r.dinner_low) + '&ndash;' + money(r.dinner_high); }
   h += '</p><p>'+weekHtml(r)+'</p>';
   if(r.short){ h += '<p>'+r.short+'</p>'; }
   h += '</div>';
  }
  el.innerHTML = h;
 }
 function bind(id, fn){
  var b = document.getElementById(id);
  if(!b) return;
  b.addEventListener('click', function(){
   fn(b);
   draw();
  });
 }
 var chips = document.querySelectorAll('[data-filter]');
 for(var i=0;i<chips.length;i++){
  (function(b){
   b.addEventListener('click', function(){
    var key = b.getAttribute('data-filter');
    var val = b.getAttribute('data-value');
    if(key === 'state' || key === 'seat'){
     var on = f[key] === val;
     f[key] = on ? '' : val;
     var sibs = document.querySelectorAll('[data-filter="'+key+'"]');
     for(var j=0;j<sibs.length;j++){ sibs[j].setAttribute('aria-pressed', 'false'); }
     b.setAttribute('aria-pressed', on ? 'false' : 'true');
    } else {
     f[key] = !f[key];
     b.setAttribute('aria-pressed', f[key] ? 'true' : 'false');
    }
    draw();
   });
  })(chips[i]);
 }
 draw();
})();
"""


def two_page(nodes, d, shell, write):
    rows = [{k: r[k] for k in ("id", "name", "city", "state", "seating", "picon", "picon_price",
                               "dinner_low", "dinner_high", "open", "closed", "founded", "short")}
            for r in d["places"]]
    js = (TWO_JS.replace("__DATA__", json.dumps(rows, ensure_ascii=False))
                .replace("__SEATLAB__", json.dumps(SEAT_LABEL, ensure_ascii=False)))
    seat = d["seating"]
    body = """
<p class="eyebrow">A table for two</p>
<h1>A table for two</h1>
<p class="lede">Basque dining rooms in the West were boarding houses, and a boarding house seats
everybody at one table. Some still do. Pick what you want and the list answers from the records.</p>
<div class="chips">
 <button class="chip" data-filter="state" data-value="CA" aria-pressed="false">California</button>
 <button class="chip" data-filter="state" data-value="NV" aria-pressed="false">Nevada</button>
 <button class="chip" data-filter="state" data-value="ID" aria-pressed="false">Idaho</button>
 <button class="chip" data-filter="seat" data-value="own" aria-pressed="false">Our own table</button>
 <button class="chip" data-filter="seat" data-value="shared" aria-pressed="false">Sit us with strangers</button>
 <button class="chip" data-filter="picon" data-value="1" aria-pressed="false">Makes a Picon Punch</button>
 <button class="chip" data-filter="today" data-value="1" aria-pressed="false">Open <span id="today-name">today</span></button>
 <button class="chip" data-filter="price" data-value="1" aria-pressed="false">Prints its prices</button>
</div>
<p><b id="two-count">%d</b> rooms.</p>
<div class="cols" id="two-results"></div>
<hr>
<h2>What the chips can and cannot do</h2>
%s
<p class="note">%d of %d rooms publish nothing about seating, so they answer neither
<i>our own table</i> nor <i>sit us with strangers</i> and drop out of both. Closing that is
ordinary work — a phone call each — and it is listed on <a href="/gaps/">Gaps</a>.</p>
<p>The <i>open today</i> chip reads your own clock and matches it against days a source published.
A day nobody published never counts as open.</p>
<script>%s</script>
""" % (len(rows),
       viz.three_state_bar(seat, "How the houses seat two people",
                           ["own", "both", "shared", "bar", "unknown"],
                           {"own": "your own table", "both": "both", "shared": "a long table",
                            "bar": "a counter", "unknown": "not published"}),
       seat.get("unknown", 0), len(rows), js)
    write("/two/", shell("A table for two — Basque Tables", body,
                          "Filter Basque dining rooms by seating, state, Picon Punch and whether they are open today.",
                          "/two/"))


# ---------------------------------------------------------------- node pages
def node_page(n, nodes, d, shell, write):
    srcs = C.sources()
    names = n["names"]
    t = n["type"]
    head = ['<p class="eyebrow">%s</p><h1>%s</h1>' % (C.esc(type_word(t)), C.esc(names["name"]))]
    if LANG == "eu":
        head.append('<p class="note" lang="eu">%s</p>' % C.esc(t_("prose_note")))
    if names.get("eu") and names["eu"].lower() != names["name"].lower():
        head.append('<p class="lede">%s%s</p>' % (
            C.esc(names["eu"]), " · said %s" % C.esc(names["said"]) if names.get("said") else ""))
    text = n.get("text") or {}
    if text.get("short"):
        head.append('<p class="lede">%s</p>' % C.esc(text["short"]))

    facts = []

    def fact(label, value, blk=None):
        if value:
            facts.append("<dt>%s</dt><dd>%s%s</dd>" % (label, value, tier_tag(blk)))

    ad = n.get("address") or {}
    if ad:
        where = ", ".join(x for x in [ad.get("street"), ad.get("city"), ad.get("state"), ad.get("zip")] if x)
        fact(t_("where"), C.esc(where), ad)
        if ad.get("phone"):
            fact(t_("phone"), '<a href="tel:%s">%s</a>' % (C.esc(ad["phone"].replace(" ", "")), C.esc(ad["phone"])))
        if ad.get("url"):
            fact(t_("own_site"), '<a href="%s" rel="nofollow">%s</a>' % (C.esc(ad["url"]), C.esc(ad["url"])))
    fo = n.get("founded") or {}
    if fo.get("year"):
        v = str(fo["year"]) + (" · " + C.esc(fo["by"]) if fo.get("by") else "")
        if fo.get("note"):
            v += "<br><span style='color:var(--ink2)'>%s</span>" % C.esc(fo["note"])
        fact(t_("opened"), v, fo)
    st = n.get("status") or {}
    if st.get("state"):
        v = {"open": t_("open"), "closed": t_("closed"), "moving": t_("moving"),
             "unknown": t_("not_established")}[st["state"]]
        if st.get("since"):
            v += " %s" % C.esc(st["since"])
        if st.get("note"):
            v += "<br><span style='color:var(--ink2)'>%s</span>" % C.esc(st["note"])
        if st.get("checked"):
            v += "<br><span style='color:var(--ink3)'>%s %s</span>" % (t_("checked"), C.esc(st["checked"]))
        fact(t_("status"), v, st)
    se = n.get("seating") or {}
    if se.get("kind"):
        v = SEAT_LABEL[se["kind"]]
        if se.get("reservations") and se["reservations"] != "unknown":
            v += " · %s %s" % (t_("reservations"), t_({"required": "required", "taken": "taken",
                                                       "walk-in": "walkin"}.get(se["reservations"], "not_published")))
        if se.get("note"):
            v += "<br><span style='color:var(--ink2)'>%s</span>" % C.esc(se["note"])
        fact(t_("seating"), v, se)
    pc = n.get("picon") or {}
    if pc.get("served"):
        v = PICON_LABEL[pc["served"]]
        if pc.get("price"):
            v += " · %s" % C.money(pc["price"])
        if pc.get("amer"):
            v += " · poured with %s" % C.esc(pc["amer"])
        if pc.get("note"):
            v += "<br><span style='color:var(--ink2)'>%s</span>" % C.esc(pc["note"])
        fact('<a href="/drink/picon-punch/" style="color:inherit">Picon Punch</a>', v, pc)
    pr = n.get("prices") or {}
    if pr.get("items"):
        rows = "".join("<tr><td>%s</td><td style='text-align:right'>%s</td></tr>"
                       % (C.esc(i["item"]), C.money(i["usd"])) for i in pr["items"])
        v = "<table style='max-width:22rem'>%s</table>" % rows
        if pr.get("includes"):
            v += "<p style='margin:.4rem 0 0;color:var(--ink2);font-size:.95rem'>Each carries %s.</p>" % C.esc(pr["includes"])
        fact(t_("dinner"), v, pr)
    ho = n.get("hours") or {}
    if ho:
        row = next((r for r in d["places"] if r["id"] == n["id"]), None)
        v = week(row) if row else ""
        if ho.get("text"):
            v += "<br>%s" % C.esc(ho["text"])
        if ho.get("checked"):
            v += "<br><span style='color:var(--ink3)'>%s %s</span>" % (t_("checked"), C.esc(ho["checked"]))
        fact(t_("week"), v, ho)
    et = n.get("etymology") or {}
    if et.get("root"):
        v = "%s%s" % (C.esc(et["root"]), " — %s" % C.esc(et["gloss"]) if et.get("gloss") else "")
        if et.get("language"):
            v += " <span style='color:var(--ink3)'>(%s)</span>" % C.esc(et["language"])
        fact(t_("root"), v, et)
    if n.get("courses"):
        fact(t_("what_arrives"), "<br>".join(C.esc(c) for c in n["courses"]))
    for r in n.get("recognitions", []):
        fact(t_("recognized"), "%s — %s%s" % (C.esc(r["by"]), C.esc(r["what"]),
                                          ", %d" % r["year"] if r.get("year") else ""))
    kt = n.get("x_kitchen") or {}
    if kt.get("says"):
        fact(t_("calls_kitchen"), "&ldquo;%s&rdquo;" % C.esc(kt["says"]), kt)

    body = ["".join(head), hero(n)]
    if facts:
        body.append('<dl class="facts">%s</dl>' % "".join(facts))
    for key, label in (("today", t_("now")), ("table", t_("at_the_table")),
                       ("history", t_("before")), ("note", t_("note"))):
        if text.get(key):
            body.append("<h2>%s</h2><p>%s</p>" % (label, C.esc(text[key])))
    for s in n.get("sections", []):
        body.append("<h2>%s%s</h2><p>%s</p>" % (C.esc(s["heading"]), tier_tag(s), C.esc(s["body"])))
    rc = n.get("recipe") or {}
    if rc.get("ingredients"):
        body.append("<h2>" + t_("build") + "</h2><ul>%s</ul>" % "".join("<li>%s</li>" % C.esc(i) for i in rc["ingredients"]))
        if rc.get("method"):
            body.append("<ol>%s</ol>" % "".join("<li>%s</li>" % C.esc(m) for m in rc["method"]))
        if rc.get("license"):
            body.append('<p class="src">%s%s</p>' % (C.esc(rc["license"]), tier_tag(rc)))

    ims = n.get("images") or []
    if len(ims) > 1:
        first = next((i for i in ims if i.get("primary")), ims[0])
        body.append(gallery([i for i in ims if i is not first], t_("pictures")))

    if t == "region":
        st = {"california": "CA", "nevada": "NV", "idaho": "ID"}.get(n["id"])
        mine = [r for r in d["places"] if r["state"] == st]
        if mine:
            trs = "".join("<tr><td><a href='/place/%s/'>%s</a></td><td>%s</td><td>%s</td><td>%s</td>"
                          "<td>%s</td><td>%s</td></tr>"
                          % (r["id"], C.esc(r["name"]), C.esc(r["city"] or ""),
                             C.esc(SEAT_SHORT[r["seating"]]), price_cell(r),
                             PICON_LABEL[r["picon"]], week(r))
                          for r in sorted(mine, key=lambda r: (r["city"] or "", r["sort"])))
            body.append('<h2>The rooms (%d)</h2><div class="tbl-scroll"><table>'
                        '<thead><tr><th>Room</th><th>Town</th><th>Seating</th><th>Dinner</th>'
                        '<th>Picon</th><th>Week</th></tr></thead><tbody>%s</tbody></table></div>'
                        % (len(mine), trs))

    kin = n.get("kin", [])
    backs = [b for b in d["backlinks"].get(n["id"], []) if b["id"] not in {k["id"] for k in kin}]
    if kin or backs:
        li = []
        for k in kin:
            other = nodes.get(k["id"])
            if not other:
                continue
            reply = next((b["how"] for b in other.get("kin", []) if b["id"] == n["id"]), None)
            li.append("<li><a href='%s'>%s</a> — %s%s</li>"
                      % (url(other), C.esc(other["names"]["name"]), C.esc(k["how"]),
                         "<br><span>&larr; and back: %s</span>" % C.esc(reply) if reply else ""))
        for b in backs:
            other = nodes.get(b["id"])
            if other:
                li.append("<li><a href='%s'>%s</a> — <span>points here: %s</span></li>"
                          % (url(other), C.esc(other["names"]["name"]), C.esc(b["how"])))
        body.append('<h2>%s</h2><ul class="kin">%s</ul>' % (t_("kin"), "".join(li)))

    if n.get("needs_verification"):
        body.append('<div class="gap"><b>%s</b><ul>%s</ul></div>'
                    % (t_("open_questions"),
                       "".join("<li>%s</li>" % C.esc(q) for q in n["needs_verification"])))

    li = []
    for sid in n.get("sources", []):
        s = srcs.get(sid, {})
        li.append("<li><a href='%s' rel='nofollow'>%s</a> — %s, %s · read %s</li>"
                  % (C.esc(s.get("url", "")), C.esc(s.get("title", sid)), C.esc(s.get("publisher", "")),
                     C.esc(s.get("kind", "")), C.esc(s.get("read", ""))))
    body.append('<h2>%s</h2><ul class="src">%s</ul>' % (t_("sources"), "".join(li)))
    body.append('<p class="src">Record provenance: %s · confidence %s · updated %s</p>'
                % (n["provenance"], n["confidence"], n["updated"]))

    ld = {"@context": "https://schema.org", "@type": "Restaurant" if t == "place" else "Article",
          "name": names["name"], "url": C.SITE_URL.rstrip("/") + url(n)}
    if t == "place":
        if ad.get("street"):
            ld["address"] = {"@type": "PostalAddress", "streetAddress": ad.get("street"),
                             "addressLocality": ad.get("city"), "addressRegion": ad.get("state"),
                             "postalCode": ad.get("zip"), "addressCountry": "US"}
        if ad.get("phone"):
            ld["telephone"] = ad["phone"]
        ld["servesCuisine"] = "Basque"
        if pr.get("dinner_low"):
            ld["priceRange"] = "%s–%s" % (C.money(pr["dinner_low"]), C.money(pr["dinner_high"]))
    else:
        ld["headline"] = names["name"]
        ld["author"] = {"@type": "Person", "name": C.BYLINE}
    write(url(n), shell("%s — Basque Tables" % names["name"], "".join(body),
                        text.get("short", names["name"]), url(n), jsonld=[ld]))


def type_index(kind, nodes, d, shell, write):
    types = C.vocab("types")
    items = C.by_type(nodes, kind)
    cards = []
    for n in items:
        ad = n.get("address") or {}
        where = ", ".join(x for x in [ad.get("city"), ad.get("state")] if x)
        cards.append('<div class="card"><h3><a href="%s">%s</a></h3>%s<p>%s</p></div>'
                     % (url(n), C.esc(n["names"]["name"]),
                        "<p>%s</p>" % C.esc(where) if where else "",
                        C.esc((n.get("text") or {}).get("short", ""))))
    label = t_({"dish": "dishes", "drink": "drinks", "term": "words", "person": "people",
                "org": "orgs", "event": "events", "story": "stories",
                "region": "regions"}.get(kind, "rooms")) if LANG == "eu" else types[kind]["label"]
    body = ('<p class="eyebrow">%s</p><h1>%s</h1><p class="lede">%s. %d.</p><div class="cols">%s</div>'
            % (C.esc(label), C.esc(label), C.esc(types[kind]["blurb"]), len(items), "".join(cards)))
    write(TYPE_INDEX[kind], shell("%s — %s" % (label, t_("site_name")), body,
                                  types[kind]["blurb"], TYPE_INDEX[kind]))


# ---------------------------------------------------------------- numbers
def numbers_page(nodes, d, shell, write):
    p = d["prices"]
    rows = d["places"]
    yrs = d["years"]
    body = """
<p class="eyebrow">Numbers</p><h1>Count it up</h1>
<p class="lede">Everything here counts records. Where a count would need a fact nobody published,
the page says so instead of estimating it.</p>
<div class="stat">
 <div><span>Records</span><b class="big">%d</b></div>
 <div><span>Rooms</span><b class="big">%d</b></div>
 <div><span>Oldest door</span><b class="big">%s</b></div>
 <div><span>Widest pair, miles</span><b class="big">%s</b></div>
</div>
%s
<figcaption>One room publishes a dinner price we could read — %d of %d. The rest print no prices
online, or print the menu as a picture. Closing that gap takes a phone call each.</figcaption>
<p>Two people ordering the cheapest and the dearest thing on the one fully published list
spend <b>%s</b> before the Picon, and the Picon at that bar is <b>$8</b>.</p>
%s
<figcaption>Rooms that publish a founding year: %d of %d. A red dot is a room that has closed.</figcaption>
%s
%s
<h2>How far apart</h2>
<p>Closest pair of towns holding rooms in different states: <b>%s miles</b>. Widest pair anywhere
in the set: <b>%s miles</b> — Chino to Boise. Both computed from town centroids, which is why they
are given to the mile and not the yard. Three states, one migration, and a day's drive between
most of it.</p>
""" % (d["counts"]["records"], d["counts"]["by_type"]["place"],
       yrs["oldest"] or "—", "{:,}".format(d["distance"]["widest_pair_mi"] or 0),
       viz.price_ladder(p["items"]), p["rooms_with_a_price"], len(rows),
       "%s and %s" % (C.money(p["low"]), C.money(p["high"])),
       viz.year_timeline(rows), yrs["rooms_with_a_year"], len(rows),
       viz.three_state_bar(d["seating"], "How the houses seat two people",
                           ["own", "both", "shared", "bar", "unknown"],
                           {"own": "your own table", "both": "both", "shared": "a long table",
                            "bar": "a counter", "unknown": "not published"}),
       viz.week_strip(d["days"]),
       "{:,}".format(d["distance"]["nearest_west_to_ohio_mi"] or 0),
       "{:,}".format(d["distance"]["widest_pair_mi"] or 0))
    write("/numbers/", shell("Numbers — Basque Tables", body,
                             "Prices, seating, published days and founding years, counted from the records.",
                             "/numbers/"))


# ---------------------------------------------------------------- gaps
def gaps_page(nodes, d, shell, write):
    cov = d["coverage"]
    labels = {"hours": "publishes its days", "seating": "says how it seats two",
              "picon": "says whether it pours a Picon", "prices": "publishes a price",
              "founded": "publishes a founding year", "address": "has an address"}
    rows = "".join("<tr><td>%s</td><td style='text-align:right'>%d</td><td style='text-align:right'>%d</td></tr>"
                   % (labels[k], v["have"], v["of"] - v["have"]) for k, v in cov.items())
    qs = "".join("<li><a href='/place/%s/'>%s</a> — %s</li>" % (q["id"], C.esc(q["name"]), C.esc(q["q"]))
                 if any(n["id"] == q["id"] and n["type"] == "place" for n in nodes.values())
                 else "<li>%s — %s</li>" % (C.esc(q["name"]), C.esc(q["q"]))
                 for q in d["open_questions"])
    body = """
<p class="eyebrow">Gaps</p><h1>What is missing</h1>
<p class="lede">A directory that hides its holes is a directory you cannot check. Here are ours,
counted.</p>
<div class="tbl-scroll"><table>
<thead><tr><th>Field</th><th style="text-align:right">Rooms with it</th><th style="text-align:right">Without</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="note">Every one of these closes with a phone call and a note of who answered.
None of them closes by guessing.</p>
<h2>Open questions, by record</h2>
<ol class="src">%s</ol>
<h2>Rooms we have not reached</h2>
<p>%d rooms in this directory come from a published directory row and nothing else — an address,
a phone number, a name. They are here because leaving them out would misrepresent how many
Basque rooms these three states hold. Their status reads <b>not established</b> and they are
excluded from every filter that would put two people in a car.</p>
""" % (rows, qs, len([r for r in d["places"] if r["status"] == "unknown"]))
    write("/gaps/", shell("Gaps — Basque Tables", body,
                          "What this directory does not know, counted field by field.", "/gaps/"))


# ---------------------------------------------------------------- wander
def wander_page(nodes, d, shell, write):
    ids = json.dumps([url(n) for n in nodes.values()])
    js = ("(function(){var U=__U__;function go(){location.href=U[Math.floor(Math.random()*U.length)];}"
          "document.getElementById('roll').addEventListener('click',go);"
          "document.addEventListener('keydown',function(e){if(e.key==='r'||e.key==='R')go();});})();"
          ).replace("__U__", ids)
    body = """
<p class="eyebrow">Wander</p><h1>Take a ride</h1>
<p class="lede">%d records. Press the button, or press <b>r</b> anywhere on the site.</p>
<p><button class="chip" id="roll" style="font-size:1.1rem;padding:.8rem 1.4rem">Somewhere &rarr;</button></p>
<script>%s</script>
""" % (len(nodes), js)
    write("/wander/", shell("Wander — Basque Tables", body, "A random record.", "/wander/"))


# ---------------------------------------------------------------- search
SEARCH_JS = """
(function(){
 var D = __DOCS__;
 var box = document.getElementById('q');
 var out = document.getElementById('hits');
 function norm(s){ return (s||'').toLowerCase().replace(/[^a-z0-9 ]+/g,' '); }
 var idx = D.map(function(d){ return {d:d, k:norm(d.name + ' ' + d.town + ' ' + d.text)}; });
 function run(){
  var q = norm(box.value).trim();
  if(!q){ out.innerHTML = ''; return; }
  var terms = q.split(/\\s+/);
  var hits = [];
  for(var i=0;i<idx.length;i++){
   var score = 0, k = idx[i].k;
   for(var j=0;j<terms.length;j++){
    var t = terms[j];
    if(k.indexOf(' '+t) >= 0 || k.indexOf(t+' ') === 0) score += 3;
    else if(k.indexOf(t) >= 0) score += 2;
    else if(t.length > 3 && k.indexOf(t.slice(0, t.length-1)) >= 0) score += 1;
   }
   if(score) hits.push({s:score, d:idx[i].d});
  }
  hits.sort(function(a,b){ return b.s - a.s; });
  if(!hits.length){ out.innerHTML = '<div class="gap">Nothing matched. Try a town, a dish, or a word.</div>'; return; }
  var h = '';
  for(var i=0;i<Math.min(hits.length, 30);i++){
   var d = hits[i].d;
   var tier = hits[i].s >= 3*terms.length ? 'read straight' : 'read loosely';
   h += '<li><a href="/'+d.type+'/'+d.id+'/">'+d.name+'</a> <span style="color:var(--ink3)">'
      + d.type + (d.town ? ' &middot; ' + d.town : '') + ' &middot; ' + tier + '</span></li>';
  }
  out.innerHTML = '<ul class="kin">' + h + '</ul>';
 }
 box.addEventListener('input', run);
 run();
})();
"""


def search_page(nodes, d, shell, write):
    js = SEARCH_JS.replace("__DOCS__", json.dumps(d["search"], ensure_ascii=False))
    body = """
<p class="eyebrow">Search</p><h1>Search</h1>
<p class="lede">Spell it however you spell it. Every hit says whether it was read straight or read loosely.</p>
<p><input type="search" id="q" placeholder="picon, Elko, tongue, etxe&hellip;" autofocus
 style="width:min(30rem,100%%)"></p>
<div id="hits"></div>
<script>%s</script>
""" % js
    write("/search/", shell("Search — Basque Tables", body, "Search the directory.", "/search/"))


# ---------------------------------------------------------------- machine files
def machine(nodes, d, shell, write):
    lines = ["# %s" % C.SITE_NAME, "",
             "> A directory of Basque dining rooms in California, Nevada and Idaho. Every field names its source.",
             "", "## How to read a record",
             "- provenance tier: cited (a named source says it), harvested (a directory row),",
             "  tradition (what the trade says, untested), inference (reasoning from records here), field (seen).",
             "- seating, picon, prices, hours, status and address may NEVER carry tier tradition or inference.",
             "- hours have three states: open, closed, and not published. A day nobody published is",
             "  excluded from every filter rather than guessed either way.", "",
             "## Data", "- /api/places.json — every room, flat",
             "- /api/counts.json — counts by type and state", "- /api/coverage.json — what is missing",
             "- /api/prices.json — every printed menu price", "- /api/search.json — search documents", "",
             "## Pages"]
    for n in sorted(nodes.values(), key=lambda x: (x["type"], C.sort_key(x))):
        lines.append("- [%s](%s): %s" % (n["names"]["name"], C.SITE_URL.rstrip("/") + url(n),
                                         (n.get("text") or {}).get("short", "")[:160]))
    with open(os.path.join(C.BUILD, "llms.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    urls = ["/", "/two/", "/places/", "/numbers/", "/gaps/", "/wander/", "/search/", "/pictures/"]
    urls += sorted(set(TYPE_INDEX[n["type"]] for n in nodes.values()))
    urls += [url(n) for n in nodes.values()]
    urls += ["/eu" + u for u in list(urls)]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("<url><loc>%s</loc></url>" % (C.SITE_URL.rstrip("/") + u))
    sm.append("</urlset>")
    with open(os.path.join(C.BUILD, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(sm) + "\n")

    with open(os.path.join(C.BUILD, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % C.SITE_URL.rstrip("/"))

    os.makedirs(os.path.join(C.BUILD, "api"), exist_ok=True)
    for name in ("places", "counts", "coverage", "prices", "search", "seating", "days"):
        with open(os.path.join(C.BUILD, "api", name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(d[name], fh, indent=1, ensure_ascii=False)

    body = ('<p class="eyebrow">404</p><h1>No table here</h1>'
            '<p class="lede">That address is not in the directory. Try <a href="/places/">the rooms</a>, '
            '<a href="/search/">search</a>, or <a href="/wander/">wander</a>.</p>')
    with open(os.path.join(C.BUILD, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(shell("Not found — Basque Tables", body, "Not found.", "/404.html"))


def render_all(nodes, d, shell, write):
    n = 0
    front(nodes, d, shell, write); n += 1
    places_page(nodes, d, shell, write); n += 1
    two_page(nodes, d, shell, write); n += 1
    numbers_page(nodes, d, shell, write); n += 1
    gaps_page(nodes, d, shell, write); n += 1
    wander_page(nodes, d, shell, write); n += 1
    search_page(nodes, d, shell, write); n += 1
    pictures_page(nodes, d, shell, write); n += 1
    for kind in TYPE_INDEX:
        if kind == "place":
            continue
        if any(x["type"] == kind for x in nodes.values()):
            type_index(kind, nodes, d, shell, write); n += 1
    for node in nodes.values():
        node_page(node, nodes, d, shell, write); n += 1
    if LANG == "en":
        machine(nodes, d, shell, write)
    return n


# ---------------------------------------------------------------- pictures
def pictures_page(nodes, d, shell, write):
    rows = []
    for n in sorted(nodes.values(), key=C.sort_key):
        for im in n.get("images") or []:
            rows.append((n, im))
    by_lic = {}
    for _, im in rows:
        by_lic[im.get("license", "?")] = by_lic.get(im.get("license", "?"), 0) + 1
    cards = []
    for n, im in rows:
        cards.append('<figure class="shot"><a href="%s"><img src="%s" alt="%s" loading="lazy" decoding="async"></a>'
                     '<figcaption><a href="%s">%s</a><br>%s<br><span class="cred">%s</span></figcaption></figure>'
                     % (C.esc(url(n)), C.esc(img_src(im)), C.esc(im.get("alt") or ""),
                        C.esc(url(n)), C.esc(n["names"]["name"]),
                        C.esc((im.get("alt") or "")[:120]), credit(im)))
    lic = " · ".join("%s %d" % (k, v) for k, v in sorted(by_lic.items()))
    with_pics = len({n["id"] for n, _ in rows})
    body = """
<p class="eyebrow">%s</p><h1>%s</h1>
<p class="lede">%d pictures on %d of %d records. Every one is CC0, public domain, CC BY, CC BY-SA
or FAL, and carries its photographer and its licence here and in a sidecar file beside the image.</p>
<p class="src">%s</p>
<div class="shots">%s</div>
<h2>Where they come from</h2>
<p>All of them from Wikimedia Commons, pulled by <code>tools/harvest_commons.py</code>, which reads the
licence off each file and refuses anything that is not free to reuse. Share-alike is complied with, not
dodged: the licence and the photographer ride with the file and are printed beside it.</p>
<p>What is thin: almost no free photograph exists of the inside of an American Basque dining room.
The Commons material is strong on the Basque Country itself, on the Boise block, and on the sheep
camps — and nearly silent on Bakersfield, Elko and Gardnerville interiors. That gap is
<a href="/gaps/">on the gaps page</a>, not papered over with a stock photograph.</p>
""" % (t_("pictures"), t_("pictures"), len(rows), with_pics, len(nodes), C.esc(lic), "".join(cards))
    write("/pictures/", shell("%s — %s" % (t_("pictures"), t_("site_name")), body,
                              "Freely licensed Basque pictures, each with its photographer and licence.",
                              "/pictures/"))
