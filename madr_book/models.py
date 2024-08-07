from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


@table_registry.mapped_as_dataclass
class Romancistas:
    __tablename__ = 'romancistas'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
    )

    livros: Mapped[List['Livros']] = relationship(
        'Livros',
        init=False,
        back_populates='autor',
        cascade='all, delete-orphan',
    )


@table_registry.mapped_as_dataclass
class Livros:
    __tablename__ = 'livros'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    titulo: Mapped[str] = mapped_column(unique=True)
    ano: Mapped[int]
    autor_id: Mapped[int] = mapped_column(ForeignKey('romancistas.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
    )

    autor: Mapped[Romancistas] = relationship(
        'Romancistas',
        init=False,
        back_populates='livros',
    )
