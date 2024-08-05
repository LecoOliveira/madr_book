from http import HTTPStatus


def test_create_user(client):
    response = client.post(
        '/conta/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_user_already_exists(client, user):
    response = client.post(
        '/conta/',
        json={
            'username': f'{user.username}',
            'email': 'example@example.com',
            'password': 'test',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username já consta no MADR'}


def test_email_already_exists(client, user):
    response = client.post(
        '/conta/',
        json={
            'username': 'test',
            'email': f'{user.email}',
            'password': 'test',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email já consta no MADR'}


def test_update_user(client, user, token):
    response = client.put(
        f'/conta/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test',
            'id': user.id,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'test',
        'email': 'test@test.com',
        'id': user.id,
    }


def test_update_wrong_user(client, other_user, token):
    response = client.put(
        f'/conta/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Não autorizado'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/conta/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Conta deletada com sucesso'}


def test_delete_user_errado(client, other_user, token):
    response = client.delete(
        f'/conta/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Não autorizado'}
