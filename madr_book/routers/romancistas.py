from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_book.database import get_session
from madr_book.models import Romancistas, User
from madr_book.schemas import (
    Message,
    RomancistaList,
    RomancistaPublic,
    RomancistaSchema,
)
from madr_book.security import get_current_user
from madr_book.settings import sanitize

router = APIRouter(prefix='/romancista', tags=['romancista'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get(
    '/{id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
def listar_romancista(id: int, user: T_CurrentUser, session: T_Session):
    romancista = session.scalar(
        select(Romancistas).where((Romancistas.id == id))
    )

    if not romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não consta no MADR',
        )
    return romancista


@router.get('/', status_code=HTTPStatus.OK, response_model=RomancistaList)
def listar_romancistas(
    user: T_CurrentUser,
    session: T_Session,
    nome: str | None = None,
    offset: str | None = None,
    limit: str | None = None,
):
    query = select(Romancistas)

    if nome:
        query = query.filter(Romancistas.nome.contains(sanitize(nome)))

    romancistas = session.scalars(query.offset(offset).limit(limit)).all()

    return {'romancistas': romancistas}


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=RomancistaPublic,
)
def criar_romancista(
    user: T_CurrentUser,
    session: T_Session,
    romancista: RomancistaSchema,
):
    db_romancista = Romancistas(nome=sanitize(romancista.nome))
    romancista_ = session.scalar(
        select(Romancistas).where((Romancistas.nome == romancista.nome))
    )

    if romancista_:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancista já consta no MADR'
        )

    session.add(db_romancista)
    session.commit()
    session.refresh(db_romancista)

    return db_romancista


@router.patch(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=RomancistaPublic,
)
def alterar_romancista(
    romancista_id: int,
    user: T_CurrentUser,
    session: T_Session,
    romancista: RomancistaSchema
):
    romancista_ = session.scalar(
        select(Romancistas).where((Romancistas.id == romancista_id))
    )
    nome_ = session.scalar(
        select(Romancistas).where(
            (Romancistas.nome == sanitize(romancista.nome))
        )
    )

    if not romancista_:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não consta no MADR',
        )

    if nome_:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Romancista já consta no MADR',
        )

    for chave, valor in romancista.model_dump(exclude_unset=True).items():
        setattr(romancista_, chave, sanitize(valor))

    session.add(romancista_)
    session.commit()
    session.refresh(romancista_)

    return romancista_


@router.delete(
    '/{romancista_id}',
    status_code=HTTPStatus.OK,
    response_model=Message
)
def deletar_romancista(
    romancista_id: int,
    user: T_CurrentUser,
    session: T_Session
):
    romancista = session.scalar(
        select(Romancistas).where((Romancistas.id == romancista_id))
    )

    if not romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Romancista não consta no MADR'
        )

    session.delete(romancista)
    session.commit()

    return {'message': 'Romancista deletado do MADR'}
