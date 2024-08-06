from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_book.database import get_session
from madr_book.models import Romancistas, User
from madr_book.schemas import RomancistaPublic, RomancistaSchema
from madr_book.security import get_current_user
from madr_book.settings import sanitize

router = APIRouter(prefix='/romancista', tags=['romancista'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=RomancistaPublic,
)
def create_romancista(
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
