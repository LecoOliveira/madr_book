from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_book.database import get_session
from madr_book.models import User
from madr_book.schemas import Message, UserPublic, UserSchema
from madr_book.security import get_current_user, get_password_hash
from madr_book.settings import sanitize

router = APIRouter(prefix='/conta', tags=['conta'])
T_Session = Annotated[Session, Depends(get_session)]
T_current_user = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == sanitize(user.username))
            | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username já consta no MADR',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email já consta no MADR',
            )
    db_user = User(
        username=sanitize(user.username),
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_current_user
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Não autorizado'
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_current_user,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Não autorizado'
        )
    session.delete(current_user)
    session.commit()

    return {'message': 'Usuário deletado'}
