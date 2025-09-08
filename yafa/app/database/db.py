import os

from util.categorize import naive_categorize_transaction
from model.BaseModel import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import model.SimpleFINModel as sf_model

# from Model.BudgetModel import Budget
# from model.CategoryModel import Category

if os.environ.get("DOCKER_MODE", False):
    DB_PATH = os.environ.get("DOCKER_DB_PATH", "sqlite:////yafa/app/data/yafaDB.db")
else:
    DB_PATH = os.environ.get("LOCAL_DB_PATH", "sqlite:///data/yafaDB.db")


def init_db() -> None:
    engine = create_engine(DB_PATH, echo=True, future=True)
    Base.metadata.create_all(engine)


def populate_db(data: dict) -> None:
    engine = create_engine(DB_PATH, echo=True, future=True)

    session = Session(engine)
    for account_data in data.get("accounts", []):
        org_data = account_data.get("org", [])

        org = session.get(sf_model.Org, org_data["domain"])
        if not org:
            org = sf_model.parse_org_data(org_data) if org_data else None
            session.add(org)
            session.commit()

        account = session.get(sf_model.Account, (org.domain, account_data["id"]))
        if not account:
            account = sf_model.parse_account_data(account_data)
            session.add(account)
            session.commit()

        for transaction_data in account_data.get("transactions", []):
            transaction = session.get(sf_model.Transaction, (org.domain, account.id, transaction_data["id"]))
            if not transaction:
                transaction = sf_model.parse_transaction_data(transaction_data, account, org)
                session.add(transaction)
                session.commit()


def auto_categorize_transactions(fn=naive_categorize_transaction) -> None:
    engine = create_engine(DB_PATH, echo=True, future=True)
    session = Session(engine)

    transactions = session.query(sf_model.Transaction).all()
    for transaction in transactions:
        if not transaction.payee and not transaction.description:
            continue  # Skip if both payee and description are None

        category = fn(
            payee=transaction.payee or "",
            description=transaction.description or ""
        )
        print(f"Transaction ID: {transaction.id}, Payee: {transaction.payee}, Description: {transaction.description}, Category: {category}")

    session.close()