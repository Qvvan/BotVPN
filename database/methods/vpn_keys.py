from datetime import datetime

from sqlalchemy.orm import Session

from models.models import VPNKeys


class VPNKeyMethods:
    def __init__(self, session: Session):
        self.session = session

    def update_vpn_key(self, vpnkey: VPNKeys):
        existing_key = self.session.query(VPNKeys).filter_by(id=vpnkey.id).first()

        if existing_key:
            existing_key.issued_at = vpnkey.issued_at
            existing_key.is_active = vpnkey.is_active
            existing_key.is_blocked = vpnkey.is_blocked
            existing_key.updated_at = datetime.now()

            self.session.commit()
            return True
        return False

    def get_vpn_key(self):
        vpn_key = self.session.query(VPNKeys).filter_by(is_active=False, is_blocked=False).first()
        return vpn_key
