from sqlalchemy.orm import Session

from models.models import Services


class ServiceMethods:
    def __init__(self, session: Session):
        self.session = session

    def get_services(self):
        services = self.session.query(Services).all()
        return services

    def add_service(self, name: str, duration_days: int, price: int):
        new_service = Services(
            name=name,
            duration_days=duration_days,
            price=price
        )
        self.session.add(new_service)
        self.session.commit()
        return new_service
