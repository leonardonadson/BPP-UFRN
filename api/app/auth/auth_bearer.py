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
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """Valida o token da requisição."""
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(status_code=403, detail="Código de autorização inválido.")

        if not credentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Esquema de autenticação inválido.")

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=403, detail="Token inválido ou expirado.")

        return credentials.credentials

    def verify_jwt(self, jwtoken: str) -> bool:
        """Verifica se o token JWT é válido."""
        payload = decode_jwt(jwtoken)
        return payload is not None


def get_current_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    Decodifica o token, busca o usuário no banco de dados e o retorna.
    Esta função é uma dependência que pode ser injetada em qualquer endpoint
    para obter o usuário autenticado atualmente.
    """
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token inválido ou expirado")

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(status_code=403, detail="Token inválido: identificador de usuário ausente")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=403, detail="Token inválido: formato de identificador de usuário incorreto")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return user