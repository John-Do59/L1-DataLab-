import json
import scrapy
from scraper.items import StandingItem
from scraper.common import DEFAULT_HEADERS


class StandingsSpider(scrapy.Spider):
    name = "l1_standings"
    allowed_domains = ["ma-api.ligue1.fr"]

    def start_requests(self):
        # 1 = Ligue 1
        url = "https://ma-api.ligue1.fr/championship-standings/1/general"
        yield scrapy.Request(
            url=url,
            method="GET",
            headers=DEFAULT_HEADERS,
            callback=self.parse_standings,
        )

    def parse_standings(self, response):
        data = json.loads(response.text)
        standings_dict = data.get("standings", {})

        for rank, details in standings_dict.items():
            item = StandingItem()
            item["rank"] = int(rank)
            item["club_id"] = details.get("clubId")
            
            # Les infos du club sont aussi dans clubIdentity
            club_info = details.get("clubIdentity", {})
            item["club_name"] = club_info.get("name")
            
            # Statistiques
            item["played"] = details.get("played")
            item["wins"] = details.get("wins")
            item["draws"] = details.get("draws")
            item["losses"] = details.get("losses")
            item["goals_for"] = details.get("forGoals")
            item["goals_against"] = details.get("againstGoals")
            item["goal_diff"] = details.get("goalsDifference")
            item["points"] = details.get("points")
            
            yield item
