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
            'password': 'test'
        }
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username já consta no MADR'}


def test_email_already_exists(client, user):
    response = client.post(
        '/conta/',
        json={
            'username': 'test',
            'email': f'{user.email}',
            'password': 'test'
        }
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email já consta no MADR'}
