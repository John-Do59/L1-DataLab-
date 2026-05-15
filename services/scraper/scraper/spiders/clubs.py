import json
import scrapy
from scraper.items import ClubItem
from scraper.common import DEFAULT_HEADERS


class ClubsSpider(scrapy.Spider):
    name = "l1_clubs"
    allowed_domains = ["ma-api.ligue1.fr"]

    def start_requests(self):
        url = "https://ma-api.ligue1.fr/championship-clubs"
        yield scrapy.Request(
            url=url,
            method="GET",
            headers=DEFAULT_HEADERS,
            callback=self.parse_clubs,
        )

    def parse_clubs(self, response):
        data = json.loads(response.text)

        # La structure réelle est {"championshipsClubs": {"id1": {...}, "id2": {...}}}
        clubs_dict = data.get("championshipsClubs", {})
        
        for club_id, club in clubs_dict.items():
            champs = club.get("championships", {})
            
            # FILTRE : On ne garde que les clubs qui participent à la Ligue 1 (ID 1)
            if "1" not in champs:
                continue
                
            item = ClubItem()
            item["club_id"] = club.get("id")
            item["name"] = club.get("name")
            item["short_name"] = club.get("shortName")
            item["city"] = club.get("city")
            item["stadium"] = club.get("stadiumId") or club.get("stadiumName")
            # Les assets (logos) sont souvent dans championships["1"] ou championships["16"]
            champs = club.get("championships", {})
            # On cherche le premier championnat disponible si "1" n'existe pas
            l1_champ = champs.get("1") or champs.get("16") or next(iter(champs.values())) if champs else {}
            assets = l1_champ.get("assets", {})
            logo_assets = assets.get("logo", {})
            
            item["logo_url"] = logo_assets.get("medium") or logo_assets.get("small") or club.get("logoUrl")
            item["primary_color"] = club.get("primaryColor")
            item["secondary_color"] = club.get("secondaryColor")
            
            yield item
