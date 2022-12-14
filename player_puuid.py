import imp
import requests, sys
from time import time
from utils import RequestError, headers, API_URL_RU, ACCEPTED_ERRORS, retry_execute


def get_player_puuid(player_name :str) -> str:
    req_url = f"/lol/summoner/v4/summoners/by-name/{player_name}"
    response = requests.get(API_URL_RU + req_url, headers=headers)

    if response.status_code == 200:
        return response.json()["puuid"]
    elif response.status_code in ACCEPTED_ERRORS:
        retry_execute(response, get_player_puuid, player_name)
    else:
        raise RequestError(response)


def main():
    try:
        player_name = sys.argv[1]
    except IndexError:
        raise Exception("Please write player name in args")

    file_name = "txt/player_puuid.txt"
    with open(file_name, "w") as file:
        file.write(get_player_puuid(player_name))
        print(f"Puuid successfully received and saved in /{file_name}.")


if __name__ == "__main__":
    main()