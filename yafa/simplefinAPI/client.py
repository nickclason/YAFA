import os
import requests
import util.utilities as utils

def fetch_accounts(days: int = int(os.environ.get("DEFAULT_DAYS_TO_FETCH"))) -> dict:
    params = {"start-date": utils.get_start_epoch(days)}
    try:
        response = requests.get(os.environ.get("SIMPLEFIN_BASE_URL"), 
                                params=params, 
                                auth=(os.environ.get("SIMPLEFIN_USERNAME"), os.environ.get("SIMPLEFIN_PASSWORD")))
        response.raise_for_status()
        data = response.json()

        # Uncomment to dump json data
        # with open("/yafa/app/data/accounts.json", "w") as f:
        #     json.dump(data, f, indent=4)

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching accounts: {e}")
        # TODO: do better :)
        return {}