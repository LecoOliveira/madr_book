from http import HTTPStatus


def test_registrar_livro(client, token, romancista):
    response = client.post(
        '/livro/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': '1991',
            'titulo': 'Testando livro',
            'autor_id': romancista.id
        }
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'ano': '1991',
        'titulo': 'testando livro',
        'autor_id': romancista.id,
        'id': 1
    }


def test_registro_livro_sem_autor_id(client, token):
    response = client.post(
        '/livro/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': '1991',
            'titulo': 'Testando livro',
            'autor_id': 1
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Romancista com o ID 1 não existe'}


def test_livro_ja_existe(client, token, livro):
    response = client.post(
        '/livro/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': '1991',
            'titulo': 'Teste livro',
            'autor_id': 1
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': f'Livro com o título {livro.titulo} já existe'
    }


def test_atualiza_livro(client, token, livro):
    response = client.patch(
        f'/livro/{livro.id}',
        json={'ano': '2000'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['ano'] == '2000'


def test_atualiza_livro_sem_livro(client, token, livro):
    response = client.patch(
        '/livro/2',
        json={'ano': '2000'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro não consta no MADR'}


def test_atualiza_livro_titulo_repetido(client, token, livro):
    response = client.patch(
        f'/livro/{livro.id}',
        json={'titulo': f'{livro.titulo}'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Livro já consta no MADR'}


def test_delete_livro(client, token, livro):
    response = client.delete(
        f'/livro/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Livro deletado no MADR'}


def test_erro_delete_livro(client, token, livro):
    response = client.delete(
        '/livro/2',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro não consta no MADR'}
