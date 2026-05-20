import json
import scrapy
from scraper.items import MatchItem
from scraper.common import DEFAULT_HEADERS


class MatchesSpider(scrapy.Spider):
    name = "l1_matches"
    allowed_domains = ["ma-api.ligue1.fr"]

    def __init__(self, season="2024", *args, **kwargs):
        super(MatchesSpider, self).__init__(*args, **kwargs)
        self.season = season  # '2024' = 24/25 season

    def start_requests(self):
        # La Ligue 1 compte 18 équipes, donc 34 journées
        for gw in range(1, 35):
            url = f"https://ma-api.ligue1.fr/championship-matches/championship/1/game-week/{gw}?season={self.season}"
            
            yield scrapy.Request(
                url=url,
                method="GET",
                headers=DEFAULT_HEADERS,
                callback=self.parse_matches,
                meta={'season': self.season, 'gameweek': gw}
            )

    def parse_matches(self, response):
        data = json.loads(response.text)
        matches = data.get("matches", [])

        for match in matches:
            item = MatchItem()
            item["match_id"] = match.get("matchId")
            
            # Gestion des données imbriquées 'home' et 'away'
            home_data = match.get("home", {})
            away_data = match.get("away", {})
            
            # Les IDs des équipes sont parfois 'clubId' ou imbriqués dans 'clubIdentity'
            item["home_team_id"] = home_data.get("clubId")
            item["away_team_id"] = away_data.get("clubId")
            
            item["kickoff"] = match.get("date")
            item["stadium"] = match.get("stadiumId")
            item["competition_id"] = match.get("championshipId")
            
            # Saison : On reformate '2024' en '2024/25' pour la consistance en DB
            year = int(response.meta['season'])
            item["season"] = f"{year}/{str(year+1)[-2:]}"
            
            item["gameweek"] = match.get("gameWeekNumber") or response.meta['gameweek']
            item["status"] = match.get("period")
            
            # Scores (None si le match n'est pas encore joué)
            item["home_score"] = home_data.get("score")
            item["away_score"] = away_data.get("score")
            
            yield item
