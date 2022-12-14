import requests, json, time, sys
from tqdm import tqdm, trange

from utils import RequestError, headers, API_URL_EUROPE, ACCEPTED_ERRORS, retry_execute
from player_matches import get_player_matches


MATCHES_LIST_FILE_NAME = "json/matches_list.json"


def get_new_puuids(match_id :str) -> list:
    match_req_url = f"/lol/match/v5/matches/{match_id}"
    match_response = requests.get(API_URL_EUROPE + match_req_url, headers=headers)

    if match_response.status_code == 200:
        return match_response.json()["metadata"]["participants"]
    elif match_response.status_code in ACCEPTED_ERRORS:
        retry_execute(match_response, get_new_puuids, match_id)
    else:
        raise RequestError(match_response)


def collect_matches(iter :int):
    with open(MATCHES_LIST_FILE_NAME, "r") as file:
        current_matches = json.load(file)

    puuids = get_new_puuids(current_matches[-1])
    
    for i in trange(iter, desc="Iteration"):
        for puuid in tqdm(puuids, desc="Processing", leave=False):
            matches = get_player_matches(puuid, 100)
            for match in matches:
                if match not in current_matches:
                    current_matches.append(match)  
            time.sleep(1.25)
        puuids = get_new_puuids(current_matches[-1]) 

    with open(MATCHES_LIST_FILE_NAME, "w") as file:
        json.dump(current_matches, file, indent=4)

if __name__ == "__main__":
    try:
        iter_count = sys.argv[1]
    except IndexError:
        raise Exception("Please write iter count in args")
    collect_matches(int(iter_count))