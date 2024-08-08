from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr_book.database import get_session
from madr_book.models import Livros, Romancistas, User
from madr_book.schemas import (
    LivroList,
    LivroPublic,
    LivroSchema,
    LivroUpdate,
    Message,
)
from madr_book.security import get_current_user
from madr_book.settings import sanitize

router = APIRouter(prefix='/livro', tags=['livro'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/{id}', status_code=HTTPStatus.OK, response_model=LivroPublic)
def listar_livro(id: int, user: T_CurrentUser, session: T_Session,):
    livro = session.scalar(select(Livros).where((Livros.id == id)))

    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR',
        )

    return livro


@router.get('/', status_code=HTTPStatus.OK, response_model=LivroList)
def listar_livros( # noqa
    user: T_CurrentUser,
    session: T_Session,
    ano: int | None = None,
    titulo: str | None = None,
    autor_id: int | None = None,
    offset: int | None = 0,
    limit: int | None = 20,
):
    query = select(Livros)
    if ano:
        query = query.where((Livros.ano == ano))
    if titulo:
        query = query.where((Livros.titulo == titulo))
    if autor_id:
        query = query.where((Livros.autor_id == autor_id))

    livros = session.scalars(query.offset(offset).limit(limit)).all()

    return {'livros': livros}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=LivroPublic)
def criar_livro(user: T_CurrentUser, session: T_Session, livro: LivroSchema):
    romancista = session.scalar(
        select(Romancistas).where((Romancistas.id == livro.autor_id))
    )
    livro_ = session.scalar(
        select(Livros).where((Livros.titulo == livro.titulo))
    )

    if livro_:
        raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Livro com o título {livro.titulo} já existe',
            )

    if not romancista:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Romancista com o ID {livro.autor_id} não existe',
        )

    db_livro = Livros(
        ano=livro.ano,
        titulo=sanitize(livro.titulo),
        autor_id=livro.autor_id,
    )

    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)

    return db_livro


@router.patch('/{livro_id}', response_model=LivroPublic)
def atualiza_livro(
    livro_id: int,
    session: T_Session,
    user: T_CurrentUser,
    livro: LivroUpdate,
):
    livro_ = session.scalar(select(Livros).where((Livros.id == livro_id)))
    titulo = session.scalar(
        select(Livros).where((Livros.titulo == livro.titulo))
    )

    if not livro_:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro não consta no MADR'
        )

    if titulo:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Livro já consta no MADR'
        )

    for chave, valor in livro.model_dump(exclude_unset=True).items():
        if isinstance(valor, str):
            valor_sanitizado = sanitize(valor)
        setattr(livro_, chave, valor_sanitizado)

    session.add(livro_)
    session.commit()
    session.refresh(livro_)

    return livro_


@router.delete('/{livro_id}', response_model=Message)
def deletar_livro(livro_id: int, session: T_Session, user: T_CurrentUser):
    livro = session.scalar(select(Livros).where((Livros.id == livro_id)))

    if not livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Livro não consta no MADR'
        )

    session.delete(livro)
    session.commit()

    return {'message': 'Livro deletado no MADR'}
