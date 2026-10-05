import requests

SPORTS_DB_URL = "https://www.thesportsdb.com/api/v1/json/3/searchteams.php"


def get_team_logo(team_name: str) -> str:
    response = requests.get(
        SPORTS_DB_URL,
        params={"t": team_name},
        timeout=5,
    )

    teams = response.json()["teams"]

    if not teams:
        return ""

    return teams[0]["strLogo"] or ""


def get_event_logos(event_name: str) -> str | None:
    team_1, team_2 = event_name.split(" v ")
    logo_1 = get_team_logo(team_1)
    logo_2 = get_team_logo(team_2)

    if not logo_1 and not logo_2:
        return None

    return f"{logo_1}|{logo_2}"
