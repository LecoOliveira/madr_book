from http import HTTPStatus


def test_cria_romancista(client, token):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Testando Romancista'}
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'nome': 'testando romancista', 'id': 1}


def test_cria_romancista_se_ja_existe(client, token, romancista):
    response = client.post(
        '/romancista/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': f'{romancista.nome}'}
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Romancista já consta no MADR'}


def test_lista_romancista_por_id(client, token, romancista):
    response = client.get(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'nome': romancista.nome,
        'id': romancista.id
    }


def test_lista_romancistas_por_nome(client, token, romancista):
    response = client.get(
        f'/romancista/?nome={romancista.nome}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'romancistas': [
            {
                'nome': romancista.nome,
                'id': romancista.id
            }
        ]
    }


def test_lista_romancistas_por_id_erro(client, token):
    response = client.get(
        '/romancista/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não consta no MADR'}


def test_atualiza_romancista(client, token, romancista):
    response = client.patch(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Nome Atualizado'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'nome': 'nome atualizado',
        'id': 1
    }


def test_atualiza_romancista_sem_romancista(client, token):
    response = client.patch(
        '/romancista/1',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Nome Atualizado'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não consta no MADR'}


def test_atualiza_romancista_nome_ja_existe(client, token, romancista):
    response = client.patch(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'test romancista'}
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Romancista já consta no MADR'}


def test_delete_romancista(client, token, romancista):
    response = client.delete(
        f'/romancista/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Romancista deletado do MADR'}


def test_delete_romancista_sem_romancista(client, token):
    response = client.delete(
        '/romancista/1',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Romancista não consta no MADR'}
