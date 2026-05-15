import json
import scrapy
from scraper.items import MatchItem
from scraper.common import DEFAULT_HEADERS


class MatchesSpider(scrapy.Spider):
    name = "l1_matches"
    allowed_domains = ["ma-api.ligue1.fr"]

    def start_requests(self):
        # On peut ajuster daysLimit pour récupérer plus de matchs
        url = "https://ma-api.ligue1.fr/championships-daily-calendars/matches"
        params = {
            "timezone": "Europe/Paris",
            "daysLimit": "7",  # Récupérer sur une semaine
            "lookAfter": "true",
        }
        
        # Construction de l'URL avec les params
        full_url = f"{url}?timezone={params['timezone']}&daysLimit={params['daysLimit']}&lookAfter={params['lookAfter']}"
        
        yield scrapy.Request(
            url=full_url,
            method="GET",
            headers=DEFAULT_HEADERS,
            callback=self.parse_matches,
        )

    def parse_matches(self, response):
        data = json.loads(response.text)
        results = data.get("results", {})
        matches_dict = results.get("matches", {})

        for match_id, match in matches_dict.items():
            item = MatchItem()
            item["match_id"] = match.get("matchId")
            item["home_team_id"] = match.get("homeTeamId")
            item["away_team_id"] = match.get("awayTeamId")
            item["kickoff"] = match.get("date")
            item["stadium"] = match.get("stadiumId")
            item["competition_id"] = match.get("championshipId")
            item["season"] = match.get("season")
            item["gameweek"] = match.get("gameWeekNumber")
            item["status"] = match.get("period")
            
            # Scores (si disponibles)
            score = match.get("score") or {}
            item["home_score"] = score.get("home")
            item["away_score"] = score.get("away")
            
            yield item
