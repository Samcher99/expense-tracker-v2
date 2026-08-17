from app.database.db_users import User
from app.core.security import get_password_hash


def test_create_user_in_db(db_session):
    new_user = User(
        email="pytest_test@example.com",
        hashed_password=get_password_hash("test123"),
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    assert new_user.id is not None
    assert new_user.email == "pytest_test@example.com"