import dotenv
import os
import simplefinAPI.client as sf_client
import database.db as db

def main():
    if not os.environ.get("IS_DOCKER", False):
        dotenv.load_dotenv()

    db.init_db()
    data = sf_client.fetch_accounts()
    if data:
        db.populate_db(data) # TODO: some sort of error handling/alert if no data


if __name__ == "__main__":
    main()
