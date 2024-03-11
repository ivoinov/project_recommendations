from app.models import Token
from app.repositories import TokenRepository
from datetime import timedelta
from app.config import settings
from datetime import datetime
from jose import jwt


class TokenService:
    def __init__(self, token_repository: TokenRepository):
        self.token_repository = token_repository

    def create_access_token(self, data, expires_delta=None):
        token = Token(**data)
        encoded_jwt = jwt.encode(
            data, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        token.token = encoded_jwt
        if expires_delta is None or not Token.expires_at:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            Token.expires_at = datetime.utcnow() + expires_delta
        self.token_repository.create(token)
        return token

    def update_expired_token(self, user_id, expires_delta=None):
        if not expires_delta:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = self.token_repository.get_by_user_id(user_id)
        token.expires_at = datetime.now() + expires_delta
        self.token_repository.update(token)
        return token

    def verify_token(self, token):
        token = self.token_repository.get_by_token(token)
        if not token or token.expires_at < datetime.utcnow():
            return False
        return True
