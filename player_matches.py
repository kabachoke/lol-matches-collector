import requests, json, sys
from utils import RequestError, headers, API_URL_EUROPE, ACCEPTED_ERRORS, retry_execute
from time import time

def get_player_matches(puuid :str, count :int) -> list:
    req_url = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
    query_url = f"?count={count}&type=ranked"

    response = requests.get(API_URL_EUROPE + req_url + query_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code in ACCEPTED_ERRORS:
        retry_execute(response, get_player_matches, puuid, count)
    else:
        raise RequestError(response)


def main():
    player_puuid = ""

    with open("player_puuid.txt", "r") as file:
        player_puuid = file.read()

    try:
        matches_count = sys.argv[1]
    except IndexError:
        raise Exception("Please write matches count in args (from 1 to 100)")

    file_name = "player_matches.json"
    with open(file_name, "w") as file:
        json.dump(get_player_matches(player_puuid, 100), file, indent=4)
        print(f"Player matches successfully received and saved in /{file_name}.")


if __name__ == "__main__":
    main()