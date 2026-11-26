
"""Application FastAPI pour les opérations et la gestion des items."""

import socket

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DEVELOPER = "Dev2"  # Remplacez par votre nom

# Stock de données en mémoire (utilisé par PUT /update/{id})
items = {1: {"name": "item1"}, 2: {"name": "item2"}}


class Operands(BaseModel):
    """Représente deux opérandes numériques."""

    a: float
    b: float


class ItemUpdate(BaseModel):
    """Données nécessaires pour modifier un item."""

    name: str


def get_ip() -> str:
    """Récupère l'adresse IP de l'interface réseau."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "unknown"
    finally:
        s.close()


def compute_multiply(a: float, b: float) -> dict:
    """Calcule le produit de deux nombres."""
    return {"result a*b": a * b, "developer": "Dev1"}


def compute_divide(a: float, b: float) -> dict:
    """Calcule la division de deux nombres."""
    if b == 0:
        raise HTTPException(
            status_code=400,
            detail="Division par zéro impossible",
        )
    return {"result a/b": a / b, "developer": "Dev2"}


def compute_delete(item_id: int) -> dict:
    """Prépare le message de suppression d'un item."""
    return {
        "message": f"Item {item_id} deleted successfully",
        "developer": DEVELOPER,
    }


@app.get("/")
def read_root():
    """Retourne le message de bienvenue."""
    return {"message": "it works !"}


@app.get("/addition")
def addition(a: int, b: int):
    """Retourne la somme de deux nombres."""
    return {"result a+b": a + b, "developer": "Dev1"}


@app.get("/soustraction")
def soustraction(a: int, b: int):
    """Retourne la différence de deux nombres."""
    return {"resultat": a - b}


@app.get("/greeting")
def greeting(name: str):
    """Retourne un message personnalisé et les informations réseau."""
    return {
        "message": f"Hello, {name}",
        "developer": DEVELOPER,
        "hostname": socket.gethostname(),
        "IP": get_ip(),
    }


@app.get("/multiply")
def multiply_get(a: float, b: float):
    """Calcule le produit via une requête GET."""
    return compute_multiply(a, b)


@app.post("/multiply")
def multiply_post(op: Operands):
    """Calcule le produit via une requête POST."""
    return compute_multiply(op.a, op.b)


@app.get("/divide")
def divide_get(a: float, b: float):
    """Calcule la division via une requête GET."""
    return compute_divide(a, b)


@app.post("/divide")
def divide_post(op: Operands):
    """Calcule la division via une requête POST."""
    return compute_divide(op.a, op.b)


@app.get("/items")
def list_items():
    """Retourne la liste des items."""
    return items


def apply_update(item_id: int, name: str) -> dict:
    """Met à jour le nom d'un item existant."""
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item introuvable",
        )

    items[item_id]["name"] = name

    return {
        "id": item_id,
        "item": items[item_id],
    }


@app.put("/update/{item_id}")
def update_item(item_id: int, item: ItemUpdate):
    """Met à jour un item avec la méthode PUT."""
    return apply_update(item_id, item.name)


@app.get("/update/{item_id}")
def update_item_get(item_id: int, name: str):
    """Met à jour un item avec la méthode GET."""
    return apply_update(item_id, name)


@app.get("/remove/{item_id}")
def delete_get(item_id: int):
    """Prépare la suppression d'un item via GET."""
    return compute_delete(item_id)


@app.post("/remove/{item_id}")
def delete_post(item_id: int):
    """Prépare la suppression d'un item via POST."""
    return compute_delete(item_id)


@app.delete("/remove/{item_id}")
def delete_item(item_id: int):
    """Prépare la suppression d'un item via DELETE."""
    return compute_delete(item_id)
