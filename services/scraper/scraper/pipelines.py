import json
from datetime import datetime
from pathlib import Path

class JsonWriterPipeline:
    def open_spider(self, spider):
        # On remonte de services/scraper/scraper/pipelines.py vers la racine du projet
        # pour accéder au dossier data/raw
        project_root = Path(__file__).resolve().parents[3]
        out_dir = project_root / "data" / "raw" / spider.name
        out_dir.mkdir(parents=True, exist_ok=True)
        
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
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
