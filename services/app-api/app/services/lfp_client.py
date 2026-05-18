import httpx
import json
import os
import glob
from app.core.cache import get_cache, set_cache

LFP_BASE_URL = "https://ma-api.ligue1.fr"
HEADERS = {
    "Origin": "https://ligue1.com",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

class LFPClient:
    async def _fetch(self, endpoint: str, ttl: int = 60):
        cache_key = f"lfp:{endpoint}"
        cached = await get_cache(cache_key)
        if cached:
            return cached
            
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{LFP_BASE_URL}{endpoint}", headers=HEADERS, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    await set_cache(cache_key, data, ttl)
                    return data
        except Exception as e:
            print(f"LFP fetch error: {e}")
            
        return self._get_fallback_data(endpoint)

    def _get_fallback_data(self, endpoint: str):
        if "championship-calendar" in endpoint:
            return self._load_local_json("l1_matches")
        elif "championship-standings" in endpoint:
            return self._load_local_json("l1_standings")
        return None

    def _load_local_json(self, prefix: str):
        data_dir = "/app/data/raw"
        if not os.path.exists(data_dir):
            data_dir = "../data/raw"
        try:
            files = glob.glob(f"{data_dir}/{prefix}/*.json")
            if files:
                latest = max(files, key=os.path.getctime)
                with open(latest, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _format_url(self, url: str):
        if not url: return ""
        if url.startswith("/"): return f"https://ligue1.com{url}"
        return url

    async def get_current_matchday(self):
        data = await self._fetch("/championship-calendar/1/nearest-game-weeks", ttl=30)
        
        if data and "nearestGameWeeks" in data and data["nearestGameWeeks"].get("currentGameWeek"):
            gw_info = data["nearestGameWeeks"]["currentGameWeek"]
            gw_num = str(gw_info["gameWeekNumber"])
            calendar = await self._fetch("/championship-calendar/1", ttl=60)
            clubs_data = await self._fetch("/championship-clubs", ttl=3600)
            
            clubs_map = {}
            if clubs_data and "championshipsClubs" in clubs_data:
                clubs_map = clubs_data["championshipsClubs"]

            if calendar and "gameWeeks" in calendar:
                gw_details = calendar["gameWeeks"].get(gw_num, {})
                matches = []
                for m in gw_details.get("matches", []):
                    match_obj = m.get("match", {})
                    home_id = match_obj.get("home", {}).get("clubId")
                    away_id = match_obj.get("away", {}).get("clubId")
                    
                    home_club = clubs_map.get(home_id, {})
                    away_club = clubs_map.get(away_id, {})
                    
                    home_name = home_club.get("shortName", "Home")
                    away_name = away_club.get("shortName", "Away")
                    
                    home_logo = self._format_url(home_club.get("assets", {}).get("logo", {}).get("small"))
                    away_logo = self._format_url(away_club.get("assets", {}).get("logo", {}).get("small"))
                    
                    score = match_obj.get("result", {}).get("score")
                    
                    matches.append({
                        "id": match_obj.get("id", ""),
                        "match_date": match_obj.get("date", ""),
                        "status": "played" if score else "preMatch",
                        "home_team": {"name": home_name, "logo": home_logo},
                        "away_team": {"name": away_name, "logo": away_logo},
                        "home_score": score.get("home") if score else None,
                        "away_score": score.get("away") if score else None,
                        "gameweek": int(gw_num)
                    })
                return {"gameweek": int(gw_num), "matches": matches}
        return None

    async def get_standings(self):
        data = await self._fetch("/championship-standings/1/general?season=2025", ttl=60)
        if data and isinstance(data, dict) and "standings" in data:
            result = []
            for rank_str, team in data["standings"].items():
                ident = team.get("clubIdentity", {})
                result.append({
                    "rank": int(rank_str),
                    "club_name": ident.get("shortName", ""),
                    "logo": self._format_url(ident.get("assets", {}).get("logo", {}).get("small")),
                    "played": team.get("played", 0),
                    "wins": team.get("wins", 0),
                    "draws": team.get("draws", 0),
                    "losses": team.get("losses", 0),
                    "goal_diff": team.get("goalsDifference", 0),
                    "points": team.get("points", 0)
                })
            return sorted(result, key=lambda x: x["rank"])
        elif data and isinstance(data, list):
            # It's fallback data, ensure logo exists
            for team in data:
                if not team.get("logo"):
                    # Try to map simple names to logos or use a default one
                    club_name = team.get("club_name", "").lower()
                    if "paris" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/13.png"
                    elif "marseille" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/10.png"
                    elif "lyon" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/11.png"
                    elif "lille" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/4.png"
                    elif "lens" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/6.png"
                    elif "monaco" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/142.png"
                    elif "nice" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/14.png"
                    elif "rennes" in club_name: team["logo"] = "https://ligue1.com/-/media/Project/LFP/shared/Images/Clubs/2024-2025/16.png"
                    else: team["logo"] = "https://ligue1.com/images/Logo_Ligue_1.webp"
            return sorted(data, key=lambda x: x.get("rank", 0))
        return None

    async def get_top_scorers(self):
        data = await self._fetch("/championship-players-ranking/1/scorers?season=2025", ttl=120)
        if data and "scorers" in data:
            result = []
            clubs_data = await self._fetch("/championship-clubs", ttl=3600)
            clubs_map = {}
            if clubs_data and "championshipsClubs" in clubs_data:
                clubs_map = clubs_data["championshipsClubs"]

            for scorer in data["scorers"][:10]:
                ident = scorer.get("playerIdentity", {})
                club_id = scorer.get("clubId")
                club_info = clubs_map.get(club_id, {})
                
                result.append({
                    "rank": scorer.get("rank"),
                    "firstName": ident.get("firstName", ""),
                    "lastName": ident.get("lastName", ""),
                    "goals": scorer.get("totalGoals", 0),
                    "matches": scorer.get("totalScoredMatches", 0),
                    "photo": self._format_url(ident.get("assets", {}).get("scorerPhoto", {}).get("small")),
                    "club_logo": self._format_url(club_info.get("assets", {}).get("logo", {}).get("small"))
                })
            return result
        return []

lfp_client = LFPClient()
