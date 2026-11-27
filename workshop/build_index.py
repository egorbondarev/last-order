#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка списка мастерской: workshop/maps/*.json -> workshop/index.json

Игра не может «спросить список файлов» у GitHub Pages, поэтому список
карт лежит одним файлом — index.json. Его собирает этот скрипт: локально
перед пушем или автоматически в GitHub Actions (см. ../.github/workflows).

Запуск:  python workshop/build_index.py
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(ROOT, "maps")
OUT = os.path.join(ROOT, "index.json")

FIELDS = ("v", "kind", "id", "slug", "title", "author", "theme", "created",
          "start", "spawns", "ammoSpots", "props", "objects", "pads")


def read_map(path):
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f)
    if data.get("kind") != "dm-map" or not data.get("title"):
        raise ValueError("%s — не карта Deathmatch" % os.path.basename(path))
    out = {k: data[k] for k in FIELDS if k in data}
    out.setdefault("author", "")
    out.setdefault("objects", [])
    out.setdefault("pads", [])
    slug = out.get("slug") or os.path.splitext(os.path.basename(path))[0]
    out["slug"] = slug
    out["file"] = slug + ".json"
    if not out.get("id"):
        out["id"] = slug
    return out


def main():
    names = sorted(n for n in os.listdir(MAPS) if n.endswith(".json"))
    maps = []
    for name in names:
        try:
            maps.append(read_map(os.path.join(MAPS, name)))
        except Exception as exc:  # noqa: BLE001 — одна битая карта не должна ломать список
            print("пропущено:", exc)
    maps.sort(key=lambda m: (m.get("title") or "").lower())
    payload = {"v": 1, "kind": "dm-workshop", "count": len(maps), "maps": maps}
    with io.open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print("index.json: карт %d" % len(maps))
    for m in maps:
        print("  · %s — %s (укрытий %d, техники %d, переходов %d)" % (
            m["title"], m.get("author") or "без автора",
            len(m.get("props", [])), len(m.get("objects", [])), len(m.get("pads", []))))


if __name__ == "__main__":
    main()
