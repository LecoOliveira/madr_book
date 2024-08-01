from http import HTTPStatus

import pytest
from fastapi import HTTPException
from freezegun import freeze_time

from madr_book.security import create_access_token, get_current_user


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_token_com_usuario_errado(client):
    response = client.post(
        '/auth/token',
        data={'username': 'test', 'password': 'test'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email ou senha incorretos'}


def test_token_expire_after_time(client, user):
    with freeze_time('2024-07-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2024-07-14 13:01:00'):
        response = client.put(
            f'/conta/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Não autorizado'}


def test_jwt_invalid_token(client):
    response = client.delete(
        '/conta/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_get_current_user_without_sub(client):
    token = create_access_token({'test': 'test'})
    with pytest.raises(HTTPException):
        get_current_user(token=token)

    response = client.delete(
        '/conta/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_not_user(client, user, token):
    response = client.delete(
        f'/conta/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    response_2 = client.put(
        f'/conta/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response_2.status_code == HTTPStatus.UNAUTHORIZED
    assert response_2.json() == {'detail': 'Não autorizado'}


def test_refresh_token(client, user, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'
