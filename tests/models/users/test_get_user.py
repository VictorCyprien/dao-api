import pytest
from datetime import datetime
import pytz
from mongoengine.errors import DoesNotExist, ValidationError

from api.models.user import User

def test_model_get_user(app, victor: User, sayori: User):
    search = User.get_by_id(victor.user_id)
    assert search == victor

    search = User.get_by_id(sayori.user_id)
    assert search == sayori

    with pytest.raises(DoesNotExist):
        User.get_by_id(124)


def test_model_get_user_wrong_id_format(app):
    with pytest.raises(ValidationError):
        User.get_by_id("MY_ID")

