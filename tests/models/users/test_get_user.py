from flask_sqlalchemy import SQLAlchemy
import pytest
from sqlalchemy.exc import IntegrityError

from api.models.user import User

def test_model_get_user(app, victor: User, sayori: User, db: SQLAlchemy):
    search = User.get_by_id(victor.user_id, db.session)
    assert search == victor

    search = User.get_by_id(sayori.user_id, db.session)
    assert search == sayori

    assert User.get_by_id(124, db.session) is None


def test_model_get_user_wrong_id_format(app, db: SQLAlchemy):
    assert User.get_by_id("MY_ID", db.session) is None

