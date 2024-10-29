import json
import uuid
import random
import base64
import requests
import urllib3
from requests.sessions import Session


class BaseKeyManager:
    def __init__(self, server_ip, session_cookie):
        self.server_ip = server_ip
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Cookie": f"lang=ru-RU; session={session_cookie}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        self.base_url = f"https://{server_ip}:54321/mysecreturl/panel"
        self.get_cert_api_url = f"https://{server_ip}:54321/mysecreturl/server/getNewX25519Cert"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def generate_uuid(self):
        return str(uuid.uuid4())

    def generate_port(self):
        return random.randint(10000, 65535)

    def send_request(self, session, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = session.post(url, headers=self.headers, data=json.dumps(data) if data else None, verify=False)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(
                f"Error {endpoint}: {response.status_code}, {response.text}")
        return response.json()

    def delete_key(self, key_id):
        with Session() as session:
            self.send_request(session, f"inbound/del/{key_id}")
            print(f"Key with ID {key_id} successfully deleted.")

    def update_key_status(self, key_id, status: bool):
        with Session() as session:
            data = {"id": key_id, "enable": status}
            self.send_request(session, f"inbound/update/{key_id}", data)
            print(f"Key with ID {key_id} successfully updated.")


class VlessKeyManager(BaseKeyManager):
    def get_certificate(self, session):
        cert_data = self.send_request(session, "server/getNewX25519Cert")
        if cert_data.get("success"):
            return cert_data["obj"]
        raise ValueError("Certificate generation failed.")

    def create_key(self, session):
        new_client = {
            "id": self.generate_uuid(),
            "flow": "xtls-rprx-vision",
            "email": self.generate_uuid(),
            "enable": True,
        }
        cert_data = self.get_certificate(session)
        data = {
            "port": self.generate_port(),
            "protocol": "vless",
            "settings": json.dumps({
                "clients": [new_client],
                "decryption": "none",
            }),
            "streamSettings": json.dumps({
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "dest": "google.com:443",
                    "privateKey": cert_data["privateKey"],
                    "publicKey": cert_data["publicKey"],
                    "fingerprint": "firefox",
                    "shortIds": [uuid.uuid4().hex[:8]],
                },
            }),
            "sniffing": json.dumps({
                "enabled": True,
                "destOverride": ["http", "tls"],
            }),
        }
        return self.send_request(session, "inbound/add", data)

    def manage_vless_key(self):
        with Session() as session:
            response = self.create_key(session)
            print("New VLESS key created successfully.", response)


class ShadowsocksKeyManager(BaseKeyManager):
    def generate_password(self):
        return uuid.uuid4().hex

    def create_key(self, session):
        new_client = {
            "method": "chacha20-ietf-poly1305",
            "password": self.generate_password(),
            "email": self.generate_uuid(),
            "enable": True,
        }
        data = {
            "port": self.generate_port(),
            "protocol": "shadowsocks",
            "settings": json.dumps({
                "method": "chacha20-ietf-poly1305",
                "password": new_client["password"],
            }),
            "streamSettings": json.dumps({
                "network": "tcp",
                "security": "none",
            }),
            "sniffing": json.dumps({
                "enabled": True,
                "destOverride": ["http", "tls"],
            }),
        }
        response = self.send_request(session, "inbound/add", data)
        response["password"] = new_client["password"]
        return response

    def generate_ss_link(self, port, password, method, key_id):
        user_info_base64 = base64.b64encode(f"{method}:{password}".encode()).decode()
        return f"ss://{user_info_base64}@{self.server_ip}:{port}?prefix=POST%20&type=tcp#MASKNETVPN-{key_id}"

    def manage_shadowsocks_key(self):
        with Session() as session:
            response = self.create_key(session)
            port = response["obj"].get("port")
            password = response["password"]
            method = "chacha20-ietf-poly1305"
            key_id = response["obj"].get("id")
            print("Shadowsocks link:", self.generate_ss_link(port, password, method, key_id))


# Usage example
if __name__ == "__main__":
    server_ip = "150.241.94.108"
    session_cookie = "MTcyOTk3Nzk4MHxEWDhFQVFMX2dBQUJFQUVRQUFCMV80QUFBUVp6ZEhKcGJtY01EQUFLVEU5SFNVNWZWVk5GVWhoNExYVnBMMlJoZEdGaVlYTmxMMjF2WkdWc0xsVnpaWExfZ1FNQkFRUlZjMlZ5QWYtQ0FBRUVBUUpKWkFFRUFBRUlWWE5sY201aGJXVUJEQUFCQ0ZCaGMzTjNiM0prQVF3QUFRdE1iMmRwYmxObFkzSmxkQUVNQUFBQUZQLUNFUUVDQVFWaFpHMXBiZ0VGWVdSdGFXNEF81ejr2lRCWJZc8IAFDWdX-R9wrwfVe3ri3QR_lYf2D90="

    vless_manager = VlessKeyManager(server_ip, session_cookie)
    vless_manager.manage_vless_key()

    ss_manager = ShadowsocksKeyManager(server_ip, session_cookie)
    ss_manager.manage_shadowsocks_key()
