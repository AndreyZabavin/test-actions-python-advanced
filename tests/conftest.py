import sys
import pytest
from app_parking import create_app, db
from app_parking.models import Client, Parking

sys.path.append(".")


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        client = Client(
            name="Test",
            surname="User",
            credit_card="1234",
            car_number="ABC123"
        )
        parking = Parking(
            address="Test Address",
            opened=True,
            count_places=10,
            count_available_places=10,
        )

        db.session.add_all([client, parking])
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
