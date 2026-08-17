from app.core.security import get_password_hash, verify_password


def test_verify_password_correct():
    hashed = get_password_hash("test123")
    assert verify_password("test123", hashed) is True


def test_verify_password_incorrect():
    hashed = get_password_hash("test123")
    assert verify_password("wrong_password", hashed) is False