
"""Tests unitaires de l'application FastAPI."""

import pytest

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_items():
    """Réinitialise les items avant chaque test."""
    main.items.clear()
    main.items.update({
        1: {"name": "item1"},
        2: {"name": "item2"},
    })


def test_read_root():
    """Vérifie l'endpoint racine."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "it works !"}


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (10, 4, 14),
        (5, 3, 8),
        (-5, 3, -2),
        (0, 0, 0),
        (-5, -3, -8),
    ],
)
def test_addition(a, b, expected):
    """Vérifie l'addition avec différentes valeurs."""
    response = client.get(
        "/addition",
        params={"a": a, "b": b},
    )

    assert response.status_code == 200
    assert response.json()["result a+b"] == expected


def test_soustraction():
    """Vérifie l'endpoint de soustraction."""
    response = client.get(
        "/soustraction",
        params={"a": 10, "b": 4},
    )

    assert response.status_code == 200
    assert response.json() == {"resultat": 6}


def test_soustraction_negative():
    """Vérifie une soustraction avec un résultat négatif."""
    response = client.get(
        "/soustraction",
        params={"a": 3, "b": 10},
    )

    assert response.status_code == 200
    assert response.json() == {"resultat": -7}


def test_soustraction_zero():
    """Vérifie une soustraction de nombres égaux."""
    response = client.get(
        "/soustraction",
        params={"a": 5, "b": 5},
    )

    assert response.status_code == 200
    assert response.json() == {"resultat": 0}


def test_multiply_get():
    """Vérifie la multiplication avec GET."""
    response = client.get(
        "/multiply",
        params={"a": 3, "b": 4},
    )

    assert response.status_code == 200
    assert response.json()["result a*b"] == 12


def test_multiply_post():
    """Vérifie la multiplication avec POST."""
    response = client.post(
        "/multiply",
        json={"a": 3, "b": 4},
    )

    assert response.status_code == 200
    assert response.json()["result a*b"] == 12


def test_multiply_invalid_input():
    """Vérifie le rejet d'une valeur non numérique."""
    response = client.get(
        "/multiply",
        params={"a": "bonjour", "b": 5},
    )

    assert response.status_code == 422


def test_divide_get():
    """Vérifie la division avec GET."""
    response = client.get(
        "/divide",
        params={"a": 10, "b": 2},
    )

    assert response.status_code == 200
    assert response.json()["result a/b"] == 5


def test_divide_post():
    """Vérifie la division avec POST."""
    response = client.post(
        "/divide",
        json={"a": 10, "b": 2},
    )

    assert response.status_code == 200
    assert response.json()["result a/b"] == 5


def test_divide_by_zero():
    """Vérifie que la division par zéro retourne une erreur 400."""
    response = client.get(
        "/divide",
        params={"a": 10, "b": 0},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Division par zéro impossible"


def test_list_items():
    """Vérifie la liste des éléments."""
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == {
        "1": {"name": "item1"},
        "2": {"name": "item2"},
    }


def test_update_item_put():
    """Vérifie la mise à jour avec PUT."""
    response = client.put(
        "/update/1",
        json={"name": "updated"},
    )

    assert response.status_code == 200
    assert response.json()["item"]["name"] == "updated"


def test_update_item_get():
    """Vérifie la mise à jour avec GET."""
    response = client.get(
        "/update/2",
        params={"name": "updated"},
    )

    assert response.status_code == 200
    assert response.json()["item"]["name"] == "updated"


def test_update_item_not_found():
    """Vérifie la mise à jour d'un élément inexistant."""
    response = client.put(
        "/update/999",
        json={"name": "unknown"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item introuvable"


def test_delete_get():
    """Vérifie la réponse de suppression avec GET."""
    response = client.get("/remove/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Item 1 deleted successfully"


def test_delete_post():
    """Vérifie la réponse de suppression avec POST."""
    response = client.post("/remove/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Item 1 deleted successfully"


def test_delete_item():
    """Vérifie la réponse de suppression avec DELETE."""
    response = client.delete("/remove/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Item 1 deleted successfully"


def test_greeting(monkeypatch):
    """Vérifie l'endpoint greeting."""
    monkeypatch.setattr(main, "get_ip", lambda: "127.0.0.1")

    response = client.get(
        "/greeting",
        params={"name": "Ali"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Hello, Ali"
    assert response.json()["IP"] == "127.0.0.1"


def test_greeting_network_error(monkeypatch):
    """Vérifie greeting lorsque l'adresse IP est inconnue."""
    monkeypatch.setattr(main, "get_ip", lambda: "unknown")

    response = client.get(
        "/greeting",
        params={"name": "Ali"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Hello, Ali"
    assert response.json()["IP"] == "unknown"


def test_get_ip_network_error(monkeypatch):
    """Vérifie get_ip en cas d'erreur réseau."""

    class FakeSocket:
        """Simule une socket réseau."""

        def connect(self, address):
            """Simule une erreur pendant la connexion."""
            raise OSError("Network error")

        def close(self):
            """Simule la fermeture de la socket."""

    monkeypatch.setattr(
        main.socket,
        "socket",
        lambda *args, **kwargs: FakeSocket(),
    )

    assert main.get_ip() == "unknown"


def test_get_ip_success(monkeypatch):
    """Vérifie get_ip lorsque la connexion fonctionne."""

    class FakeSocket:
        """Simule une socket réseau fonctionnelle."""

        def connect(self, address):
            """Simule une connexion réussie."""

        def getsockname(self):
            """Retourne une adresse IP simulée."""
            return ("192.0.2.1", 80)

        def close(self):
            """Simule la fermeture de la socket."""

    monkeypatch.setattr(
        main.socket,
        "socket",
        lambda *args, **kwargs: FakeSocket(),
    )

    assert main.get_ip() == "192.0.2.1"
