import os

import model.SimpleFINModel as sf_model
from util.categorize import naive_categorize_transaction
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import Session
import json


def init_db() -> None:
    if os.environ.get("DOCKER_MODE", False):
        DB_PATH = "sqlite:////yafa/data/yafaDB.db"
    else:
        DB_PATH = "sqlite:///data/yafaDB.db"
    print(f"Initializing DB at {DB_PATH}")

    engine = create_engine(DB_PATH, echo=True, future=True)
    sf_model.Base.metadata.create_all(engine)


def get_db_session() -> Session:
    if os.environ.get("DOCKER_MODE", False):
        DB_PATH = "sqlite:////yafa/data/yafaDB.db"
    else:
        DB_PATH = "sqlite:///data/yafaDB.db"

    engine = create_engine(DB_PATH, echo=True, future=True)
    session = Session(engine)
    return session


def populate_db(data: dict) -> None:
    session = get_db_session()
    for account_data in data.get("accounts", []):
        org_data = account_data.get("org", [])

        org = session.get(sf_model.Org, org_data["domain"])
        if not org:
            org = sf_model.create_org(org_data) if org_data else None
            session.add(org)
            session.commit()

        account = session.get(sf_model.Account, (org.domain, account_data["id"]))
        if not account:
            account = sf_model.create_account(account_data)
            session.add(account)
            session.commit()

        for transaction_data in account_data.get("transactions", []):
            transaction = session.get(sf_model.Transaction, (org.domain, account.id, transaction_data["id"]))
            if not transaction:
                transaction = sf_model.create_transaction(transaction_data, account, org)
                session.add(transaction)
                session.commit()

    populate_default_categories(session)
    auto_categorize_transactions(session)

    session.close()


def populate_default_categories(session: Session):
    """Insert some common budget categories if they don't already exist."""

    default_categories = json.loads(os.environ.get("DEFAULT_CATEGORIES", None))

    for type in default_categories:
        if type not in ["Income", "Expense"]:
            return
        for name in default_categories[type]:
            exists = session.scalar(
                select(sf_model.Category)
                .where(and_(
                    sf_model.Category.type == type,
                    sf_model.Category.name == name
                ))
            )

            if not exists:
                session.add(sf_model.Category(type=type, name=name))

    session.commit()


def auto_categorize_transactions(session: Session, fn=naive_categorize_transaction) -> None:
    """
    Auto-categorize all transactions using the provided categorization function.

    Args:
        session (Session): SQLAlchemy session
        fn (callable): function that takes (payee, description) and returns a category name (str or None)
    """
    transactions = session.query(sf_model.Transaction).all()

    for transaction in transactions:
        if not transaction.payee and not transaction.description:
            continue  # Skip if both payee and description are None

        category_name = fn(
            payee=transaction.payee or "",
            description=transaction.description or ""
        )

        if not category_name:
            continue  # Skip if the function returns None / can't categorize... Currently this shouldn't be possible

        # Try to fetch the category from the DB
        # TODO: this isn't exactly ideal...
        category = session.scalar(select(sf_model.Category).where(sf_model.Category.name == category_name))

        # Optionally create the category if missing
        if not category:
            category = sf_model.Category(name=category_name)  # Default to "Expense" type for new categories
            session.add(category)
            session.flush()  # ensures category.id is available

        # Assign category to transaction
        transaction.category = category

    session.commit()