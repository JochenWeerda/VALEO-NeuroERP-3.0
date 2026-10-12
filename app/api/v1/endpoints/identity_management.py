"""Server-side session management in the shared identity boundary."""
from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field
from app.auth.deps import get_current_user, require_roles
from app.core import identity_session

router=APIRouter(prefix='/identity',tags=['identity'])


class SessionOut(BaseModel):
    subject: str
    tenant_id: str
    idle_seconds: int
    absolute_seconds: int


class RevokeSubject(BaseModel):
    subject: str = Field(min_length=1,max_length=200)


@router.get('/session',response_model=SessionOut,summary='Aktuelle verifizierte Sitzung')
def current_session(request: Request,user: dict=Depends(get_current_user)) -> SessionOut:
    return SessionOut(subject=user['sub'],tenant_id=request.state.tenant_id,
        idle_seconds=identity_session.settings.IDENTITY_SESSION_IDLE_SECONDS,
        absolute_seconds=identity_session.settings.IDENTITY_SESSION_MAX_SECONDS)


@router.post('/session/logout',status_code=204,response_class=Response,response_model=None,summary='Aktuelle Sitzung serverseitig widerrufen')
def logout(request: Request,user: dict=Depends(get_current_user)) -> Response:
    identity_session.revoke_session(request.state.token_claims,request.state.authenticated_token)
    return Response(status_code=204)


@router.post('/subjects/revoke',status_code=204,response_class=Response,response_model=None,
             summary='Vorhandene Sitzungen eines Mandantenbenutzers widerrufen',dependencies=[Depends(require_roles('admin'))])
def revoke_subject(payload: RevokeSubject, request: Request) -> Response:
    identity_session.revoke_subject(request.state.token_claims['iss'],request.state.tenant_id,payload.subject,
                                   actor=request.state.token_claims['sub'])
    return Response(status_code=204)
