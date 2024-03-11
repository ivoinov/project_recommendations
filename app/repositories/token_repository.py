from app.models import Token
from app.config import settings
import datetime


class TokenRepository:
    def __init__(self, db):
        self.db = db

    def create(self, token):
        try:
            db_token = Token(token=token.token, user_id=token.user_id)
            if token.expires_at:
                db_token.expires_at = token.expires_at
            else:
                db_token.expires_at = datetime.datetime.now() + datetime.timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                )
            self.db.add(db_token)
            self.db.commit()
            self.db.refresh(db_token)
            return db_token
        except:
            self.db.rollback()
            settings.logger.exception("Error creating token")
            raise
        finally:
            self.db.close()

    def update(self, token):
        try:
            db_token = (
                self.db.query(Token).filter(Token.user_id == token.user_id).first()
            )
            db_token.token = token.token
            if token.expires_at:
                db_token.expires_at = token.expires_at
            self.db.commit()
            self.db.refresh(db_token)
            return db_token
        except:
            self.db.rollback()
            settings.logger.exception("Error updating token")
            raise
        finally:
            self.db.close()

    def get_by_user_id(self, user_id):
        return self.db.query(Token).filter(Token.user_id == user_id).first()

    def get_by_token(self, token):
        return self.db.query(Token).filter(Token.token == token).first()
