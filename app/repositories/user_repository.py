from app.models import User
from passlib.context import CryptContext
from app.config import settings


class UserRepository:
    def __init__(self, session):
        self.session = session

    def _get_password_hash(self, password):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def create(self, user):
        try:
            hashed_password = self._get_password_hash(user.password)
            db_user = User(
                email=user.email,
                hashed_password=hashed_password,
                full_name=user.full_name,
                username=user.username,
                disabled=False,
            )
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return db_user
        except Exception:
            self.session.rollback()
            settings.logger.exception("Error creating user")
            raise

    def get_user_by_email(self, email):
        return self.session.query(User).filter(User.email == email).first()

    def verify_password(self, user, password):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(password, user.hashed_password)
