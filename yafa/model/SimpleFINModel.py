from sqlalchemy import String, Float, Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .BaseModel import Base

# Org Model
class Org(Base):
    __tablename__ = "orgs"

    domain: Mapped[str] = mapped_column(String, primary_key=True)   # unique + PK
    id: Mapped[str] = mapped_column(String, default=None)           # not unique
    name: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, default=None)
    sfin_url: Mapped[str] = mapped_column(String, default=None)     # not unique

    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="org",
        cascade="all, delete-orphan"
    )


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


# Account Model
class Account(Base):
    __tablename__ = "accounts"

    org_domain: Mapped[str] = mapped_column(
        String, ForeignKey("orgs.domain"), primary_key=True
    )
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    currency: Mapped[str] = mapped_column(String, default=None)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    available_balance: Mapped[float] = mapped_column(Float, default=0.0)
    balance_date: Mapped[int] = mapped_column(Integer, default=0)

    org: Mapped["Org"] = relationship("Org", back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="account",
        cascade="all, delete-orphan"
    )


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


# Transaction Model
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

    posted: Mapped[int] = mapped_column(Integer, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str] = mapped_column(String, default=None)
    payee: Mapped[str] = mapped_column(String, default=None)
    memo: Mapped[str] = mapped_column(String, default=None)
    transacted_at: Mapped[int] = mapped_column(Integer, default=0)

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")


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


# Category Model
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, unique=False, nullable=False, default="Expense")  # or "Income"
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # monthly_budget: Mapped[float] = mapped_column(Float, default=0.0)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="category"
    )

    def is_expense(self) -> bool:
        return self.type == "Expense"
    
    def is_income(self) -> bool:
        return self.type == "Income"


# class Budget(Base):
#     __tablename__ = "budgets"
