"""Der Datenbank-Connect darf den API-Start nicht endlos blockieren."""

from app.core.database import POSTGRES_CONNECT_TIMEOUT_SECONDS, postgres_connect_args


def test_postgres_connect_timeout_is_five_seconds() -> None:
    assert POSTGRES_CONNECT_TIMEOUT_SECONDS == 5
    assert postgres_connect_args() == {"connect_timeout": 5}
