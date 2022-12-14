import json
import os

from tqdm import tqdm

FOLDER_PATH = "json/matches"

def dump_stats():
    matches_files = os.listdir(FOLDER_PATH)

    data = {}
    errors = 0
    for match_file_name in tqdm(matches_files, desc="Progress"):
        match = json.load(open(f"{FOLDER_PATH}/{match_file_name}", "r")) 
        try:
            heroes_list = []
            a = [match["100"]["TOP"]["championName"], match["200"]["TOP"]["championName"]].sort()
            a.sort()
            key_top = '_'.join()
            key_jungle = '_'.join([match["100"]["JUNGLE"]["championName"],match["200"]["JUNGLE"]["championName"]].sort())
            key_mid = '_'.join([match["100"]["MIDDLE"]["championName"], match["200"]["MIDDLE"]["championName"]].sort())
            key_bot = '_'.join([match["100"]["BOTTOM"]["championName"], match["200"]["BOTTOM"]["championName"]].sort())
            key_sup = '_'.join([match["100"]["UTILITY"]["championName"], match["200"]["UTILITY"]["championName"]].sort())
            
            if key_top in data:
                data[key_top] += 1
            else:
                data[key_top] = 1
            if key_jungle in data:
                data[key_jungle] += 1
            else:
                data[key_jungle] = 1
            if key_mid in data:
                data[key_mid] += 1
            else:
                data[key_mid] = 1
            if key_bot in data:
                data[key_bot] += 1
            else:
                data[key_bot] = 1
            if key_sup in data:
                data[key_sup] += 1
            else:
                data[key_sup] = 1
        except Exception as e:
            print(e)
            errors += 1
    
    print("Errors: ", errors)

    with open("json/stats.json", "w") as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    dump_stats()