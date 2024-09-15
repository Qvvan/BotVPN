from sqlalchemy.orm import Session

from models.models import Users


class UserMethods:
    def __init__(self, session: Session):
        self.session = session

    def user_exists(self, tg_id: str) -> bool:
        user = self.session.query(Users).filter_by(tg_id=tg_id).first()
        return user is not None

    def add_user(self, user: Users):
        if self.user_exists(user.tg_id):
            return

        self.session.add(user)
        self.session.commit()
