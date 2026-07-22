from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base: provide a shared registry that makes sqlAlchemy knows about every table
    """

    pass
