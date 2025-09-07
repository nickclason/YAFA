from sqlalchemy import String, Float, Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# TODO: Support "Holdings" (not documented anywhere?)
# TODO: Add categories to transactions


class Base(DeclarativeBase):
    pass


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

    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
