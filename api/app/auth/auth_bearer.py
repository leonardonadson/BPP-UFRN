"""Módulo de implementação do esquema de autenticação Bearer JWT."""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# LIMPEZA: Ordem de importação corrigida
from ..database import get_db
from ..models import User
from .auth_handler import decode_jwt

class JWTBearer(HTTPBearer):
    """Verifica o token JWT Bearer."""
    def __init__(self, auto_error: bool = True):
        # LIMPEZA: Refatorado para usar super() sem argumentos (padrão Python 3)
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """Valida o token da requisição."""
        # LIMPEZA: Refatorado para usar super() sem argumentos
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        # LIMPEZA: Refatorado para remover 'else' desnecessário após 'return'
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
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Token inválido ou expirado")
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=403, detail="Token inválido")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return user
