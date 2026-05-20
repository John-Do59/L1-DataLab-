import scrapy


class MatchItem(scrapy.Item):
    match_id = scrapy.Field()
    home_team_id = scrapy.Field()
    away_team_id = scrapy.Field()
    kickoff = scrapy.Field()
    stadium = scrapy.Field()
    competition_id = scrapy.Field()
    season = scrapy.Field()
    gameweek = scrapy.Field()
    status = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()


class StandingItem(scrapy.Item):
    rank = scrapy.Field()
    club_id = scrapy.Field()
    club_name = scrapy.Field()
    played = scrapy.Field()
    wins = scrapy.Field()
    draws = scrapy.Field()
    losses = scrapy.Field()
    goals_for = scrapy.Field()
    goals_against = scrapy.Field()
    goal_diff = scrapy.Field()
    points = scrapy.Field()


class ClubItem(scrapy.Item):
    club_id = scrapy.Field()
    name = scrapy.Field()
    short_name = scrapy.Field()
    city = scrapy.Field()
    stadium = scrapy.Field()
    colors = scrapy.Field()
    primary_color = scrapy.Field()
    secondary_color = scrapy.Field()
    logo_url = scrapy.Field()


class ChampionshipSettingItem(scrapy.Item):
    championship_id = scrapy.Field()
    name = scrapy.Field()
    season = scrapy.Field()
    sponsor_name = scrapy.Field()


class ArticleItem(scrapy.Item):
    article_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    published_at = scrapy.Field()
