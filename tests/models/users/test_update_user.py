from flask_sqlalchemy import SQLAlchemy

from api.models.user import User


def test_model_update_user(app, victor: User, db: SQLAlchemy):
    data_update = {
        "email": "vicvic@gmail.com",
        "discord_username": "vicvic#4321",
        "wallet_address": "0x12345654789",
    }

    assert victor.email == "victor@example.com"
    assert victor.discord_username == "victor#1234"

    victor.update(input_data=data_update)
    db.session.commit()
    db.session.refresh(victor)

    assert victor.email == "vicvic@gmail.com" and victor.email != "victor@example.com"
    assert victor.discord_username == "vicvic#4321" and victor.discord_username != "victor#1234"

    # Double check that the wallet address is not updated
    assert victor.wallet_address == "0x1234567890" and victor.wallet_address != "0x12345654789"

