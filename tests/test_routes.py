import sys
import pytest
from datetime import datetime
from app_parking.models import Client, ClientParking, Parking

sys.path.append(".")


@pytest.mark.parametrize("route", ["/clients", "/clients/1"])
def test_get_routes(client, route):
    response = client.get(route)
    assert response.status_code == 200


def test_create_client(client, db_session):
    data = {
        "name": "John",
        "surname": "Doe",
        "credit_card": "5678",
        "car_number": "XYZ789",
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    assert "id" in response.json

    new_client = Client.query.get(response.json["id"])
    assert new_client is not None
    assert new_client.name == "John"


def test_create_parking(client, db_session):
    data = {"address": "New Parking", "opened": True, "count_places": 20}
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    assert "id" in response.json

    new_parking = Parking.query.get(response.json["id"])
    assert new_parking is not None
    assert new_parking.address == "New Parking"


@pytest.mark.parking
def test_client_enter_parking(client, db_session):
    ClientParking.query.filter_by(client_id=1, parking_id=1).delete()

    parking = Parking.query.get(1)
    parking.count_available_places = 10
    db_session.commit()

    data = {"client_id": 1, "parking_id": 1}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 201

    parking = Parking.query.get(1)
    assert parking.count_available_places == 9

    new_entry = ClientParking.query.filter_by(
        client_id=1, parking_id=1, time_out=None
    ).first()
    assert new_entry is not None


@pytest.mark.parking
def test_client_exit_parking(client, db_session):
    with db_session.no_autoflush:
        ClientParking.query.filter_by(client_id=1, parking_id=1).delete()

        parking = Parking.query.get(1)
        parking.count_available_places = 10
        db_session.flush()

        entry = ClientParking(client_id=1,
                              parking_id=1,
                              time_in=datetime.utcnow())
        db_session.add(entry)
        parking.count_available_places -= 1
        db_session.flush()

    db_session.commit()

    data = {"client_id": 1, "parking_id": 1}
    response = client.delete("/client_parkings", json=data)
    assert response.status_code == 200

    parking = Parking.query.get(1)
    assert parking.count_available_places == 10

    exited_entry = (
        ClientParking.query.filter_by(client_id=1, parking_id=1)
        .order_by(ClientParking.id.desc())
        .first()
    )
    assert exited_entry.time_out is not None
