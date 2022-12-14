import time, json
from datetime import datetime

region_prefix = "europe"
platform_prefix = "ru"

API_URL_EUROPE = f"https://{region_prefix}.api.riotgames.com"
API_URL_RU = f"https://{platform_prefix}.api.riotgames.com"
API_KEY = open("txt/api_key.txt", "r").read()
ACCEPTED_ERRORS = [429, 500, 502, 503]

host = "127.0.0.1"
user = "postgres"
password = "misha"
db_name = "lol"
port = 5432

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Accept-Language" : "en-US",
    "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token" : API_KEY
}

def get_error_str(response) -> str:
    return f"Request error.\n" \
        f"\tStatus code: {response.status_code},\n" \
        f"\tHeaders: {response.headers},\n" \
        f"\tRequest url: {response.url},\n" \
        f"\tResponse content: {response.content}"


def retry_execute(response, func, *args):
    print(get_error_str(response))
    print(f"{response.status_code} ERROR OCCURED. Retrying to execute program...")

    error_time = str(datetime.now())
    log = {
        "type" : "Request error",
        "statusCode" : response.status_code,
        "requestUrl" : response.url,
        "content" : response.text
    }
    with open(f"logs/log_{error_time}.json", "w") as log_file:
        json.dump(log, log_file, indent=4)

    time.sleep(10)
    if len(args) == 1:
        func(args[0])
    elif len(args) == 2:
         func(args[0], args[1])
    elif len(args) == 3:
         func(args[0], args[1], args[2])
    

class RequestError(Exception):
    def __init__(self, response):
        self.message = get_error_str(response)
        super().__init__(self.message)