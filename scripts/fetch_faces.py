"""Download each person's Wikipedia lead photo (and its Commons license) into faces/src/."""
import json
import os
import urllib.parse
import urllib.request

PEOPLE = {
    "okan": "Okan_Buruk",
    "ismael": "Valérien_Ismaël",
    "avci": "Abdullah_Avcı",
    "bjelica": "Nenad_Bjelica",
    "gunes": "Şenol_Güneş",
    "burak": "Burak_Yılmaz",
    "calimbay": "Rıza_Çalımbay",
    "santos": "Fernando_Santos_(footballer,_born_1954)",
    "gio": "Giovanni_van_Bronckhorst",
    "ole": "Ole_Gunnar_Solskjær",
    "mourinho": "José_Mourinho",
    "tedesco": "Domenico_Tedesco",
    "sergen": "Sergen_Yalçın",
    "tekke": "Fatih_Tekke",
    "kartal": "İsmail_Kartal",
}
UA = {"User-Agent": "okan-the-barbarian/1.0 (https://github.com/kadirselcuk-cloud/okan-the-barbarian)"}
OUT = os.path.join(os.path.dirname(__file__), "..", "faces", "src")


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def lead_image(title):
    for lang in ("en", "tr"):
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "prop": "pageimages", "piprop": "thumbnail|name",
            "pithumbsize": 800, "redirects": 1, "titles": title.replace("_", " "),
        })
        pages = get_json(f"https://{lang}.wikipedia.org/w/api.php?{q}")["query"]["pages"]
        for p in pages.values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"], p["pageimage"], f"https://{lang}.wikipedia.org/wiki/{title}"
    return None, None, None


def license_info(name):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "prop": "imageinfo", "iiprop": "extmetadata",
        "titles": f"File:{name}",
    })
    pages = get_json(f"https://commons.wikimedia.org/w/api.php?{q}")["query"]["pages"]
    meta = next(iter(pages.values())).get("imageinfo", [{}])[0].get("extmetadata", {})
    pick = lambda k: meta.get(k, {}).get("value", "")
    return {"artist": pick("Artist"), "license": pick("LicenseShortName"), "licenseUrl": pick("LicenseUrl")}


def main():
    os.makedirs(OUT, exist_ok=True)
    credits = {}
    for pid, title in PEOPLE.items():
        src, name, article = lead_image(title)
        if not src:
            print(f"{pid}: no image")
            continue
        with urllib.request.urlopen(urllib.request.Request(src, headers=UA), timeout=60) as r:
            data = r.read()
        ext = os.path.splitext(urllib.parse.urlparse(src).path)[1].lower() or ".jpg"
        with open(os.path.join(OUT, pid + ext), "wb") as f:
            f.write(data)
        credits[pid] = {"file": name, "fileUrl": f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(name)}",
                        "article": article, **license_info(name)}
        print(f"{pid}: {name} ({len(data)} bytes)")
    with open(os.path.join(OUT, "credits.json"), "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
