"""Módulo de implementação do esquema de autenticação Bearer JWT."""
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# CORREÇÃO: As importações relativas '..' foram trocadas por absolutas a partir de 'app'.
from app.database import get_db
from app.models import User
# A importação abaixo está correta, pois é relativa dentro do mesmo pacote.
from .auth_handler import decode_jwt

class JWTBearer(HTTPBearer):
    """Verifica o token JWT Bearer."""
    def __init__(self, auto_error: bool = False): # <--- MUDANÇA: auto_error=False
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            # Agora este erro será lançado por nós (401) e não pelo FastAPI (403)
            raise HTTPException(status_code=401, detail="Código de autorização inválido ou ausente.")

        if not credentials.scheme == "Bearer":
            raise HTTPException(status_code=401, detail="Esquema de autenticação inválido.")

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

        return credentials.credentials

    def verify_jwt(self, jwtoken: str) -> bool:
        payload = decode_jwt(jwtoken)
        return payload is not None

def get_current_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado") # CORREÇÃO

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(status_code=401, detail="Token inválido: identificador ausente") # CORREÇÃO

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=401, # CORREÇÃO
            detail='Token inválido: formato de identificador incorreto'
        ) from exc

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado") # CORREÇÃO

    return user
