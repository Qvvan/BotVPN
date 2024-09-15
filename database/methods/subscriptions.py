from datetime import datetime

from sqlalchemy.orm import Session

from models.models import Subscriptions


class SubscriptionMethods:
    def __init__(self, session: Session):
        self.session = session

    def get_subscription(self, tg_id):
        subscription = self.session.query(Subscriptions).filter_by(tg_id=tg_id).first()
        return subscription is not None

    def create_sub(self, sub: Subscriptions):
        self.session.add(sub)
        self.session.commit()
        return True

    def update_sub(self, sub: Subscriptions):
        existing_sub = self.session.query(Subscriptions).filter_by(tg_id=sub.tg_id).first()

        if not existing_sub:
            self.create_sub(sub)
        else:
            existing_sub.service_id = sub.service_id
            existing_sub.vpn_key_id = sub.vpn_key_id
            existing_sub.start_date = sub.start_date
            existing_sub.end_date = sub.end_date
            existing_sub.updated_at = datetime.now()

            self.session.commit()

        return True
