import time
from utils import RequestError, headers, API_URL_EUROPE, ACCEPTED_ERRORS, retry_execute
import requests, json, sys


def get_hero_showings(hero_info_json : dict) -> dict:
    return {
        "championName" : hero_info_json["championName"],
        "kills" : hero_info_json["kills"],
        "deaths" : hero_info_json["deaths"],
        "assists" : hero_info_json["assists"],
        "damage" : hero_info_json["totalDamageDealtToChampions"],
        "damageTaken" : hero_info_json["totalDamageTaken"],
        "damageToBuildings" : hero_info_json["damageDealtToBuildings"] if "damageDealtToBuildings" in hero_info_json else 0, 
        "totalMinionsKilled" : hero_info_json["totalMinionsKilled"] + hero_info_json["neutralMinionsKilled"],
        "gold" : hero_info_json["goldEarned"],
        "id" : hero_info_json["participantId"],
        "championId" : hero_info_json["championId"],
        "role" : hero_info_json["teamPosition"]
    }

def get_stats(match_dict : dict, match_info : dict) -> dict:
    match_info["gameMode"] = match_dict["info"]["gameMode"]
    match_info["gameVersion"] = match_dict["info"]["gameVersion"]
    match_info["gameDurationInSeconds"] = match_dict["info"]["gameDuration"]

    participants = match_dict["info"]["participants"]
    for p in participants:
        hero = get_hero_showings(p)
        match_info[f"{p['teamId']}"][f"{p['participantId']}"] = hero

    team100_info = match_dict["info"]["teams"][0]
    team200_info = match_dict["info"]["teams"][1]

    team100_bans, team200_bans = [], []

    for ban in team100_info["bans"]:
        team100_bans.append(ban["championId"])
    for ban in team200_info["bans"]:
        team200_bans.append(ban["championId"])

    match_info["100"]["isWin"] = team100_info["win"]
    match_info["200"]["isWin"] = team200_info["win"]

    match_info["100"]["bans"] = team100_bans
    match_info["200"]["bans"] = team200_bans

    match_info["100"]["objectives"] = team100_info["objectives"]
    match_info["200"]["objectives"] = team200_info["objectives"]

    return match_info


def get_timeline_stats(match_timeline, match_info):
    BREAK_POINT = 17 # data will collect at 17 min of match
    if len(match_timeline["info"]["frames"]) > BREAK_POINT:
        heroes = match_timeline["info"]["frames"][BREAK_POINT]["participantFrames"]
        laning_stats_field = f"laningStats_{BREAK_POINT}_min"
        for key, val in zip(list(heroes.keys()), list(heroes.values())):
            match_info["100" if int(key) < 6 else "200"][key][laning_stats_field] = {
                "kills" : 0,
                "deaths" : 0,
                "assists" : 0,
                "damage" : val["damageStats"]["totalDamageDoneToChampions"],
                "damageTaken" : val["damageStats"]["totalDamageTaken"],
                "level" : val["level"],
                "jungleMinionsKilled" : val["jungleMinionsKilled"],
                "minionsKilled" : val["minionsKilled"],
                "gold" : val["totalGold"],
                "xp" : val["xp"]  
            }
        
        for frame in match_timeline["info"]["frames"][:BREAK_POINT]:
            for event in frame["events"]:
                if event["type"] == "CHAMPION_KILL":
                    #change killer stats
                    if event["killerId"] != 0:
                        killer_team = "100" if int(event["killerId"]) < 6 else "200"
                        killer_id = f"{event['killerId']}"
                        match_info[killer_team][killer_id][laning_stats_field]["kills"] = \
                            int(match_info[killer_team][killer_id][laning_stats_field]["kills"]) + 1
                    #change killer stats

                    #change victim stats
                    victim_team = "100" if int(event["victimId"]) < 6 else "200"
                    victim_id = f"{event['victimId']}"
                    match_info[victim_team][victim_id][laning_stats_field]["deaths"] = \
                        int(match_info[victim_team][victim_id][laning_stats_field]["deaths"]) + 1
                    #change victim stats

                    #change assist stats
                    if "assistingParticipantIds" in event:
                        for assist_id in event["assistingParticipantIds"]:
                            assist_team = "100" if int(assist_id) < 6 else "200"
                            match_info[assist_team][f"{assist_id}"][laning_stats_field]["assists"] = \
                                int(match_info[assist_team][f"{assist_id}"][laning_stats_field]["assists"]) + 1
                    #change assist stats
        return match_info
    else: 
        return 0


def collect_match_data(match_id :str, match_dict :dict, match_timeline :dict) -> str:
    match_info = {
        "100" : {},
        "200" : {},
    }
    match_info = get_stats(match_dict, match_info)
    match_info = get_timeline_stats(match_timeline, match_info)

    if match_info == 0:
        return "error"

    for key, val in zip(list(match_info["100"].keys())[:5], list(match_info["100"].values())[:5]):
        match_info["100"][val["role"]] = val
        match_info["100"][val["role"]].pop("role", None)
        match_info["100"].pop(key, None)

    for key, val in zip(list(match_info["200"].keys())[:5], list(match_info["200"].values())[:5]):
        match_info["200"][val["role"]] = val
        match_info["200"][val["role"]].pop("role", None)
        match_info["200"].pop(key, None)

    file_name = f"json/matches/{match_id}_stats.json"
    with open(file_name, "w") as file:
        json.dump(match_info, file, indent=4)
    
    return file_name


def dump_player_match(match_id : str):
    match_req_url = f"/lol/match/v5/matches/{match_id}"
    match_response = requests.get(API_URL_EUROPE + match_req_url, headers=headers)

    if match_response.status_code == 200:
        match_dict = match_response.json()
    elif match_response.status_code in ACCEPTED_ERRORS:
        retry_execute(match_response, dump_player_match, match_id)
    else:
        raise RequestError(match_response)

    match_timeline_req_url = f"/lol/match/v5/matches/{match_id}/timeline"
    match_timeline_response = requests.get(API_URL_EUROPE + match_timeline_req_url, headers=headers)

    if match_timeline_response.status_code == 200:
        match_timeline = match_timeline_response.json()
    elif match_timeline_response.status_code in ACCEPTED_ERRORS:
        retry_execute(match_timeline_response, dump_player_match, match_id)
    else:
        raise RequestError(match_timeline_response)

    if not match_dict["info"]["participants"][0]["gameEndedInEarlySurrender"]:
        match_stats_file_name = collect_match_data(match_id, match_dict, match_timeline)
        if match_stats_file_name == "error":
            print(f"Bad match, parse error")
        else:
            print(f"Successfully dump match stats in {match_stats_file_name}")
    else:
        print(f"Game {match_id} is ended in early surrender")


if __name__ == "__main__":
    matches_file_name = "json/matches_list.json"
    try:
        match_count = sys.argv[1]
    except IndexError:
        raise Exception("Please write match count")
    
    with open(matches_file_name, "r") as file:
        matches = json.load(file)[2000:int(match_count)]

    for match in matches:
        dump_player_match(match)
        time.sleep(2)