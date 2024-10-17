from datetime import datetime

from flask import Blueprint, jsonify, request

from . import db
from .models import Client, ClientParking, Parking

bp = Blueprint("main", __name__)


@bp.route("/clients", methods=["GET"])
def get_clients():
    clients = Client.query.all()
    return jsonify(
        [
            {
                "id": c.id,
                "name": c.name,
                "surname": c.surname,
                "car_number": c.car_number,
            }
            for c in clients
        ]
    )


@bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify(
        {
            "id": client.id,
            "name": client.name,
            "surname": client.surname,
            "car_number": client.car_number,
        }
    )


@bp.route("/clients", methods=["POST"])
def create_client():
    data = request.json
    new_client = Client(
        name=data["name"],
        surname=data["surname"],
        credit_card=data.get("credit_card"),
        car_number=data.get("car_number"),
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"id": new_client.id}), 201


@bp.route("/parkings", methods=["POST"])
def create_parking():
    data = request.json
    new_parking = Parking(
        address=data["address"],
        opened=data["opened"],
        count_places=data["count_places"],
        count_available_places=data["count_places"],
    )
    db.session.add(new_parking)
    db.session.commit()
    return jsonify({"id": new_parking.id}), 201


@bp.route("/client_parkings", methods=["POST"])
def client_enter_parking():
    data = request.json
    client = Client.query.get_or_404(data["client_id"])
    parking = Parking.query.get_or_404(data["parking_id"])

    if not parking.opened:
        return jsonify({"error": "Parking is closed"}), 400

    if parking.count_available_places <= 0:
        return jsonify({"error": "No available parking spaces"}), 400

    existing_entry = ClientParking.query.filter_by(
        client_id=client.id, parking_id=parking.id, time_out=None
    ).first()

    if existing_entry:
        return jsonify({"error": "Client already in parking"}), 400

    new_entry = ClientParking(
        client_id=client.id, parking_id=parking.id, time_in=datetime.utcnow()
    )
    parking.count_available_places -= 1

    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"message": "Client entered parking successfully"}), 201


@bp.route("/client_parkings", methods=["DELETE"])
def client_exit_parking():
    data = request.json
    client = Client.query.get_or_404(data["client_id"])
    parking = Parking.query.get_or_404(data["parking_id"])

    entry = ClientParking.query.filter_by(
        client_id=client.id, parking_id=parking.id, time_out=None
    ).first()

    if not entry:
        return (
            jsonify({"error": "No active parking session found for this client"}),
            404,
        )

    if not client.credit_card:
        return jsonify({"error": "Client has no credit card for payment"}), 400

    entry.time_out = datetime.utcnow()
    parking.count_available_places += 1

    db.session.commit()

    return jsonify({"message": "Client exited parking successfully"})
