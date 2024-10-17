# flake8: noqa: E402

import sys

import factory # type: ignore

sys.path.append(".")
from app_parking import db
from app_parking.models import Client, Parking


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.Maybe(
        factory.Faker("pybool"),
        yes_declaration=factory.Faker("credit_card_number"),
        no_declaration=None,
    )
    car_number = factory.Faker("bothify", text="??####??")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    opened = factory.Faker("pybool")
    count_places = factory.Faker("random_int", min=10, max=100)
    count_available_places = factory.LazyAttribute(lambda o: o.count_places)


def test_create_client_with_factory(client, db_session):
    new_client = ClientFactory()
    db_session.commit()

    assert new_client.id is not None
    assert Client.query.count() == 2


def test_create_parking_with_factory(client, db_session):
    new_parking = ParkingFactory()
    db_session.commit()

    assert new_parking.id is not None
    assert Parking.query.count() == 2
