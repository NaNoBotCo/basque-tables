"""Match triaged Commons files to records by substring, and write x_commons_files.

Every pairing here is a human choice — a picture of a bean plant in Araba is not
evidence about a bowl of beans in Elko, so nothing is auto-matched by keyword across
the whole corpus. The patterns below name what was picked and for which record.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

PICKS = {
 "uberuaga-boarding-house": ["Cyrus Jacobs-Uberuaga House (1)", "Cyrus Jacobs-Uberuaga House (3)",
                             "Cyrus Jacobs-Uberuaga House (5)", "Front of Cyrus Jacobs House",
                             "Entry to Cyrus Jacobs House", "Cyrus Jacobs House, Boise"],
 "the-basque-block": ["Boise-basque-block", "Laiak, Basque Block", "Anduiza Hotel Building",
                      "Basque center in Boise", "Historical Home on Boise", "Bola Jokoa",
                      "A bench outside the Basque Museum", "A sign outside the Basque Museum"],
 "idaho": ["Basque immigrant graves", "Basque plaque in Boise", "Basque dancers in Boise"],
 "martin-hotel-winnemucca": ["Martin Hotel (Winnemucca, Nevada)"],
 "nevada": ["Gateway to the scenic west, Hotel Humboldt", "Winnemucca 1877"],
 "picon-punch": ["Picon Punch (5307913384)"],
 "artzain": ["Basque-tree-carving", "Deer aspenflat trickman", "House carving lhanson",
             "Ladys face carving lhanson", "Viva france carving lhanson", "Sheep herder wagon 7874"],
 "basque-beans": ["Alubia tolosa", "Tolosako babarrunak", "Arabako babarrun nabarraren lekatxoak"],
 "txuleta": ["Txuletak.jpg"],
 "pintxo": ["Pincho Vitoria 15", "Pincho Vitoria 16", "Pinchos bermeo 2",
            "Pintxo de pulpo con alcachofa", "Pintxos (15640616804)"],
 "croquetas": ["Pincho de tortilla de espárragos", "Pincho tortilla-34"],
 "jaialdi": ["Urkullu-Jaialdia 2015", "Basque Joaldunak Folk tradition"],
 "euskara": ["Basque notice in Boise"],
 "zazpiak-bat": ["Ikurriña en Getaria.jpg", "Funerary stèle with the basque flag"],
 "ostatua": ["Armoire basque avec lauburu", "Restaurant du col d'Osquich - Basque cupboard"],
 "etxe": ["House with lauburu in Savoie", "Lauburu sur les pavés"],
 "txoko": ["Sagardotegi baten barnealdea", "Sidreria 2", "Sagardo.JPG"],
 "the-long-table": ["Irigoien Herrero sagardotegia", "Dolarea2"],
 "txakoli": ["Txakoli"],
 "california": ["Crites Bldg, Bakersfield", "2009-0726-CA-Bakersfield-ThePadre.jpg"],
 "lamb-chops": ["Sheep herder wagon 7874"],
 "kalimotxo": ["Kalimotxo"],
 "noriega-hotel": ["Dinner Menu for Noriega Hotel Bakersfield"],
 "the-set-dinner": ["Dinner Menu for Noriega Hotel Bakersfield"],
 "gateau-basque": ["Gateau basque avec Lauburu", "Gâteau basque à la cerise noire",
                   "Gateau basque et croix basques", "Gâteau basque 01"],
 "marmitako": ["Marmitako.JPG", "Marmitako algorta 001", "Ondarroa Marmitako 2024 1"],
 "bacalao-al-pil-pil": ["BacalaoalPilpil", "Bacalao al Pil Pil (Vizcaya)", "Cocotxas al pil pil",
                        "CocotxasPilPil"],
 "idiazabal": ["2016 Smithsonian Folklife Festival Basque culture Idiazabal cheese",
               "Queso Idiazábal.jpg", "Euskal Museoa cheese", "Artzai txabola"],
 "talo": ["Bidart Taloa", "Talo Supazterrean", "Kristina Saralegi talogilea",
          "Talo (galette de maïs) servie chaude"],
 "lauburu": ["Lauburu Ganalto 01", "Cheese with lauburu 2", "Lauburu sur les pavés",
             "Armoire basque avec lauburu"],
 "ikurrina": ["Ikurriña en Getaria.jpg", "Ikurrina Andoainen, 1977ko urtarrila",
              "Funerary stèle with the basque flag"],
 "baserri": ["Amundarain baserria.jpg", "Etxeberri baserria (Anoeta)", "Goiuriako baserri bat",
             "Iztueta Berri"],
 "sagardotegi": ["Sagardotegi baten barnealdea", "Irigoien Herrero sagardotegia", "Sagardo.JPG",
                 "Txuletak.jpg"],
 "pilota": ["Bola Jokoa"],
 "txistu": ["Juanan Aroma", "Santutxuko txistulariak 1989", "Txistua bere kutxan"],
 "dantza": ["Basque dancers.jpg", "Basque dancers 01", "Basque girls dancing 001",
            "Au Pays Basque - danse", "Ezpatadantzariak"],
 "jt-basque-gardnerville": ["Downtown Gardnerville, Nevada 06-26-2012"],
 "garlic-fried-chicken": [],
 "kalimotxo": ["Kalimotxo2.jpg", "Porrón 1"],
 "patxaran": ["Patxaran casero", "Pacharán con hielo", "Patxaran des laminak 1",
              "Botella del Consejo Regulador de Pacharán Navarro", "Etxeko patxaran lehiaketa"],
 "croquetas": ["Croquetas.jpg", "Croquetas 3.JPG", "Croquetas caseras de carne de cocido",
               "Croquetas-Jamón-Riofrío"],
 "mus": ["Final de mus en el Café Iruña (1 de 13)", "Final de mus en el Café Iruña (4 de 13)",
         "Final de mus en el Café Iruña (10 de 13)"],
 "dantza": ["Aurresku a Germán1", "Acto religioso y aurresku junto a la ermita"],
 "the-basque-market": ["Cooking a paella", "Paella-mixta", "Concurso Internacional de Paella de Sueca 2016 - 44"],
 "louis-basque-corner": ["Downtown Reno, Nevada (17575523693)", "Downtown Reno, Nevada (602607158)"],
 "leku-ona": ["Boise, Idaho.jpg", "Boise Centre and downtown at night"],
 "lamb-chops": ["Grilled lamb chops.jpg", "Grilled Lamb Loin Chops-01"],
 "oxtail-stew": ["Oxtail Stew.jpg", "Oxtail stew, mashed potato and broccoli", "Coda alla vaccinara-01"],
 "bread-pudding": ["BPL Bread Pudding", "Bread Pudding 1.jpg", "Bread pudding, Arnaud's, French Quarter"],
 "pickled-tongue": ["BEEF TONGUE - LANGUE DE BŒUF", "Lengua a la vinagreta.jpg",
                    "Ox tongue with salad and fries from Gathering"],
 "ansots": ["Ardèche - Chorizo à cuire", "Chorizo ahumado (picada argentina)"],
 "villa-basque-deli": ["ChorizoBilbao"],
}


def load_triage():
    out = {}
    d = os.path.join(C.IMAGES, "_triage")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        for row in C.load_json(os.path.join(d, fn)).get("files", []):
            if row.get("free") and (row.get("width") or 0) >= 700 and \
               (row.get("mime") or "").startswith("image/") and "svg" not in (row.get("mime") or ""):
                out.setdefault(row["title"], row)
    return out


def main():
    pool = load_triage()
    nodes = C.load_nodes()
    print("%d free raster files in triage" % len(pool))
    total = 0
    for rid, pats in PICKS.items():
        n = nodes.get(rid)
        if not n:
            print("  ?  no record %s" % rid)
            continue
        hits = []
        for pat in pats:
            found = [t for t in pool if pat.lower() in t.lower()]
            if not found:
                print("  -  %s: nothing matched %r" % (rid, pat))
            hits += found[:3]
        hits = list(dict.fromkeys(hits))
        if not hits:
            continue
        n2 = {k: v for k, v in n.items() if k != "_path"}
        n2["x_commons_files"] = hits
        C.jdump(n2, n["_path"])
        total += len(hits)
        print("  ok %-28s %d" % (rid, len(hits)))
    print("%d files assigned" % total)


if __name__ == "__main__":
    raise SystemExit(main())
