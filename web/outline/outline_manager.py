from outline_vpn.outline_vpn import OutlineVPN


class OutlineManager:
    def __init__(self, api_url, cert_sha256):
        self.server = OutlineVPN(
            api_url=api_url,
            cert_sha256=cert_sha256,
        )

    async def create_key(self, user_id: str, encrypted_part: str):
        return self.server.create_key(name=user_id, key_id=encrypted_part)

    async def delete_key(self, key_id):
        return self.server.delete_key(key_id=key_id)

    async def get_keys(self):
        return self.server.get_keys()
