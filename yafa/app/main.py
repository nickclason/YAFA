

import datetime
import dotenv
# import json
from Model.Models import Base, Account, Org, Transaction
import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from Util.categorize import naive_categorize_transaction

# Docker volume is mounted to: /yafa/app/data

DB_PATH = os.environ.get("DOCKER_DB_PATH", "sqlite:////yafa/app/data/yafaDB.db") if os.environ.get("DOCKER_MODE", False) else os.environ.get("LOCAL_DB_PATH", "sqlite:///data/yafaDB.db")


def get_start_epoch(days: int) -> int:
    """Return the Unix timestamp for N days ago."""
    return int((datetime.datetime.now() - datetime.timedelta(days=days)).timestamp())


def fetch_accounts(days: int = int(os.environ.get("DEFAULT_DAYS_TO_FETCH"))) -> dict:
    """Fetch accounts from the SimpleFIN API."""
    params = {"start-date": get_start_epoch(days)}
    # print(params)
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
        return {}
    

def parse_org_data(data: dict) -> Org | None:
    org = None

    org = Org(
        id=data["id"],
        name=data["name"],
        domain=data.get("domain"),
        url=data.get("url"),
        sfin_url=data.get("sfin-url")
    )

    return org


def parse_transaction_data(data: dict, account: Account, org: Org) -> Transaction | None:
    transaction = None

    transaction = Transaction(
        account_org=org.domain,
        account_id=account.id,
        id=data["id"],
        posted=data.get("posted", 0),
        transacted_at=data.get("transacted_at", 0),
        amount=data.get("amount", 0.0),
        description=data.get("description"),
        payee=data.get("payee"),
        memo=data.get("memo"),
        # category=data.get("category"), # TODO: Add support for categories
    )

    return transaction


def parse_account_data(data: dict) -> Account | None:
    account = None

    account = Account(
        org_domain=data["org"]["domain"],
        id=data["id"],
        name=data["name"],
        currency=data.get("currency"),
        balance=data.get("balance", 0.0),
        available_balance=data.get("available-balance", 0.0),
        balance_date=data.get("balance-date", 0)
    )

    return account


def init_db() -> None:
    print(DB_PATH)
    engine = create_engine(DB_PATH, echo=True, future=True)
    Base.metadata.create_all(engine)


def populate_db(data: dict) -> None:
    engine = create_engine(DB_PATH, echo=True, future=True)

    session = Session(engine)
    for account_data in data.get("accounts", []):
        org_data = account_data.get("org", [])

        org = session.get(Org, org_data["domain"])
        if not org:
            org = parse_org_data(org_data) if org_data else None
            session.add(org)
            session.commit()

        account = session.get(Account, (org.domain, account_data["id"]))
        if not account:
            account = parse_account_data(account_data)
            session.add(account)
            session.commit()

        for transaction_data in account_data.get("transactions", []):
            transaction = session.get(Transaction, (org.domain, account.id, transaction_data["id"]))
            if not transaction:
                transaction = parse_transaction_data(transaction_data, account, org)
                session.add(transaction)
                session.commit()


def auto_categorize_transactions(fn=naive_categorize_transaction) -> None:
    engine = create_engine(DB_PATH, echo=True, future=True)
    session = Session(engine)

    transactions = session.query(Transaction).all()
    for transaction in transactions:
        if not transaction.payee and not transaction.description:
            continue  # Skip if both payee and description are None

        category = fn(
            payee=transaction.payee or "",
            description=transaction.description or ""
        )
        print(f"Transaction ID: {transaction.id}, Payee: {transaction.payee}, Description: {transaction.description}, Category: {category}")

    session.close()


def main():
    if not os.environ.get("IS_DOCKER", False):
        dotenv.load_dotenv()

    init_db()
    data = fetch_accounts()
    if data:
        print("Data dumped to /data directory.")
        populate_db(data)
    else:
        print("No data returned.")

    auto_categorize_transactions()


if __name__ == "__main__":
    main()
