from outline_vpn.outline_vpn import OutlineVPN

from outline.config_outline.secret import SERVERS


class OutlineManager:
    def __init__(self):
        self.clients = {}

        for server_id, config in SERVERS.items():
            self.clients[server_id] = OutlineVPN(api_url=config["API_URL"], cert_sha256=config["CERT_SHA256"])

    def list_servers(self):
        return {server_id: client.get_server_information()['name'] for server_id, client in self.clients.items()}

    def get_server_id_by_name(self, server_name: str):
        for server_id, name in self.list_servers().items():
            if name == server_name:
                return server_id
        return None

    def create_key(self, server_id: str):
        if server_id in self.clients:
            return self.clients[server_id].create_key(name='Свободый')
        raise ValueError(f"Server ID {server_id} not found.")

    def delete_key(self, server_id: str, key_id: str):
        if server_id in self.clients:
            return self.clients[server_id].delete_key(key_id)
        raise ValueError(f"Server ID {server_id} not found.")

