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
