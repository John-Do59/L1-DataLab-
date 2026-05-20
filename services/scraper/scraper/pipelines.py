import json
import os
from datetime import datetime
from pathlib import Path
from scrapy.exceptions import DropItem

class DuplicatesPipeline:
    """Évite de traiter deux fois le même item pendant un crawl."""
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        # On utilise match_id ou clubId comme identifiant unique
        item_id = item.get('match_id') or item.get('club_id')
        if item_id in self.ids_seen:
            raise DropItem(f"🚫 Doublon détecté et supprimé : {item_id}")
        else:
            self.ids_seen.add(item_id)
            return item

class JsonExportPipeline:
    """Pipeline existante pour l'export JSON."""
    def open_spider(self, spider):
        out_dir = Path(__file__).resolve().parents[2] / "data" / "raw" / spider.name
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%dT%H%M%S")
        self.file_path = out_dir / f"{spider.name}_{ts}.json"
        self.file = open(self.file_path, "w", encoding="utf-8")
        self.first_item = True
        self.file.write("[")

    def close_spider(self, spider):
        self.file.write("]")
        self.file.close()

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(",\n")
        self.first_item = False
        json.dump(dict(item), self.file, ensure_ascii=False, indent=2)
        return item
