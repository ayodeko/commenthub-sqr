import pytest

from api.dependencies import get_db
from sqlalchemy.orm import Session
from unittest.mock import MagicMock


def test_get_db_session():
    mock_session = MagicMock(spec=Session)

    with pytest.raises(TypeError):
        with mock_session:
            with get_db() as session:
                assert isinstance(session, Session)
            assert mock_session.close.called


def test_get_db_lifecycle():
    with next(get_db()) as db:
        assert isinstance(db, Session)


def test_get_db_exception_handling():
    with pytest.raises(Exception):
        with get_db() as db:
            assert isinstance(db, Session)
            raise Exception("Test Exception")
