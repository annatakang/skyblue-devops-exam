from unittest.mock import patch

from auth import get_password_hash, verify_password
from fake.db import dump_users, get_all_users, get_user_by_id


def test_password_hash_accepts_correct_password():
    hashed = get_password_hash("exam-password")
    assert hashed != "exam-password"
    assert verify_password("exam-password", hashed)


def test_password_hash_rejects_wrong_password():
    hashed = get_password_hash("exam-password")
    assert not verify_password("wrong-password", hashed)


def test_users_json_round_trip(tmp_path):
    users = [{
        "id": 42,
        "username": "exam-user",
        "email": "exam@example.com",
        "full_name": "Exam User",
        "user_type": "default",
        "hashed_password": get_password_hash("exam-password"),
        "created_by": 1,
    }]
    database = str(tmp_path / "users.json")
    dump_users(users, database)
    loaded = [user.dict() for user in get_all_users(database)]
    assert loaded == users


def test_user_lookup_found_and_missing(tmp_path):
    users = [{
        "id": 42,
        "username": "exam-user",
        "email": "exam@example.com",
        "full_name": "Exam User",
        "user_type": "default",
        "hashed_password": get_password_hash("exam-password"),
        "created_by": 1,
    }]
    database = str(tmp_path / "users.json")
    dump_users(users, database)
    records = list(get_all_users(database))

    with patch("fake.db.get_all_users", side_effect=lambda: iter(records)):
        assert get_user_by_id(42).username == "exam-user"
        assert get_user_by_id(999) is None
