from sqlalchemy import String, Integer, ForeignKey, ForeignKeyConstraint, UniqueConstraint, DateTime, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .BaseModel import Base

import datetime as dt

# Org Model
# https://www.simplefin.org/protocol.html#organization
class Org(Base):
    __tablename__ = "orgs"

    domain: Mapped[str] = mapped_column(String, primary_key=True)
    id: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=True)
    sfin_url: Mapped[str] = mapped_column(String, nullable=False)

    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="org",
        cascade="all, delete-orphan"
    )


def create_org(data: dict) -> Org:
    return Org(
        id=data.get("id"),
        name=data.get("name"),
        domain=data.get("domain"),
        url=data.get("url"),
        sfin_url=data.get("sfin-url")
    )


# Account Model
# https://www.simplefin.org/protocol.html#account
class Account(Base):
    __tablename__ = "accounts"

    org_domain: Mapped[str] = mapped_column(
        String, ForeignKey("orgs.domain"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    available_balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    balance_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    org: Mapped["Org"] = relationship("Org", back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan"
    )


def create_account(data: dict) -> Account:
    return Account(
        org_domain=data["org"]["domain"],
        id=data.get("id"),
        name=data.get("name"),
        currency=data.get("currency"),
        balance=data.get("balance"),
        available_balance=data.get("available-balance"),
        balance_date=dt.datetime.fromtimestamp(int(((data.get("balance-date")))))
    )



# Transaction Model
# https://www.simplefin.org/protocol.html#transaction
#
# TODO: Support "Holdings" (not documented anywhere?)
class Transaction(Base):
    __tablename__ = "transactions"

    account_org: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(String, primary_key=True)
    id: Mapped[str] = mapped_column(String, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["account_org", "account_id"],
            ["accounts.org_domain", "accounts.id"]
        ),
    )

    posted: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    payee: Mapped[str] = mapped_column(String, nullable=False)
    memo: Mapped[str] = mapped_column(String, nullable=True)
    transacted_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    pending : Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # extra ??? = mapped_column(JSON, nullable=True)  # TODO: Add support for extra data

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")


def create_transaction(data: dict, account: Account, org: Org) -> Transaction:
    return Transaction(
        account_org=org.domain,
        account_id=account.id,
        id=data["id"],
        posted=dt.datetime.fromtimestamp(int((data.get("posted")))),
        transacted_at=dt.datetime.fromtimestamp(int(data.get("transacted_at", 0))),
        amount=data.get("amount"),
        description=data.get("description"),
        payee=data.get("payee"),
        memo=data.get("memo"),
        pending=data.get("pending", False),
    )


# Category Model
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False, default="Expense")  # or "Income"
    name: Mapped[str] = mapped_column(String, nullable=False, default="Uncategorized")

    __table_args__ = (UniqueConstraint("type", "name"),)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="category"
    )

    budgets: Mapped[list["Budget"]] = relationship(
        "Budget",
        back_populates="category",
        cascade="all, delete-orphan"
    )


# Budget Model
# Not part of SimpleFIN
class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    category: Mapped["Category"] = relationship("Category", back_populates="budgets")

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    period_start: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    # optional: rollover if you want "unused budget carries forward"
    # this concept has never made sense to me personally but leaving in case i ever want to support it
    # rollover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
