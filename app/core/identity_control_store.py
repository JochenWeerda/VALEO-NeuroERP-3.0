"""Shared fail-closed storage and verified human boundary for identity administration."""
from functools import wraps
import inspect
import json
import redis
from fastapi import HTTPException
from app.core.identity_context import current_identity

def storage_boundary(function):
    if inspect.isgeneratorfunction(function):
        @wraps(function)
        def generator(*args, **kwargs):
            try:
                yield from function(*args, **kwargs)
            except redis.RedisError as exc:
                raise HTTPException(503, 'Agent control store unavailable') from exc
        return generator
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except redis.RedisError as exc:
            raise HTTPException(503, 'Agent control store unavailable') from exc
    return wrapped


def human(*, administrative: bool = False):
    principal = current_identity()
    if principal.claims.get('identity_type') != 'human':
        raise HTTPException(403, 'Verified human identity required')
    if administrative and 'admin' not in principal.roles:
        raise HTTPException(403, 'Tenant administration required')
    return principal


def read_record(client, location: str) -> dict:
    raw = client.get(location)
    if raw is None:
        raise HTTPException(404, 'Agent control object not found')
    return json.loads(raw)
