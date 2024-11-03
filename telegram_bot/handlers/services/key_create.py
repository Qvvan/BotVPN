import base64
import json
import random
import uuid

import requests
import urllib3
from requests.sessions import Session

from config_data.config import MY_SECRET_URL


class BaseKeyManager:
    def __init__(self, server_ip, session_cookie):
        self.server_ip = server_ip
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Cookie": f"lang=ru-RU; session={session_cookie}",
            "Host": f"{server_ip}:54321",
            "Origin": f"https://{server_ip}:54321",
            "Referer": f"https://{server_ip}:54321/{MY_SECRET_URL}/panel/inbounds",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.base_url = f"https://{server_ip}:54321/{MY_SECRET_URL}/panel"

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def generate_uuid(self):
        return str(uuid.uuid4())

    def generate_port(self):
        return random.randint(10000, 65535)

    def get_inbounds(self, session):
        list_api_url = f"{self.base_url}/inbound/list"
        response = session.post(list_api_url, headers=self.headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.exceptions.RequestException(
                f"Error fetching inbounds: {response.status_code}, {response.text}")

    def delete_key(self, key_id):
        with Session() as session:
            try:
                delete_api_url = f"{self.base_url}/inbound/del/{key_id}"
                response = session.post(delete_api_url, headers=self.headers, verify=False)
                if response.status_code == 200:
                    print(f"Key with ID {key_id} successfully deleted.")
                else:
                    raise requests.exceptions.RequestException(
                        f"Error deleting key: {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")

    def update_key(self, key_id, status: bool):
        with Session() as session:
            try:
                update_api_url = f"{self.base_url}/inbound/update/{key_id}"
                update_data = {
                    "id": key_id,
                    "enable": status
                }
                response = session.post(update_api_url, headers=self.headers, data=json.dumps(update_data),
                                        verify=False)
                if response.status_code == 200:
                    print(f"Key with ID {key_id} successfully updated")
                else:
                    raise requests.exceptions.RequestException(
                        f"Error updating key: {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")


class VlessKeyManager(BaseKeyManager):
    def __init__(self, server_ip, session_cookie):
        super().__init__(server_ip, session_cookie)
        self.get_cert_api_url = f"https://{server_ip}:54321/{MY_SECRET_URL}/server/getNewX25519Cert"

    def get_certificate(self, session):
        response = session.post(self.get_cert_api_url, headers=self.headers, verify=False)
        if response.status_code == 200:
            cert_data = response.json()
            if cert_data.get("success"):
                return cert_data["obj"]
            else:
                raise ValueError("Certificate generation failed.")
        else:
            raise requests.exceptions.RequestException(
                f"Error fetching certificate: {response.status_code}, {response.text}")

    def create_vless_key(self, session, new_client, private_key, public_key):
        create_api_url = f"{self.base_url}/inbound/add"
        port = self.generate_port()
        short_id = uuid.uuid4().hex[:8]
        new_vless_key_data = {
            "up": 0,
            "down": 0,
            "total": 0,
            "remark": new_client["remark"],
            "enable": True,
            "expiryTime": 0,
            "listen": "",
            "port": port,
            "protocol": "vless",
            "settings": json.dumps({
                "clients": [new_client],
                "decryption": "none",
                "fallbacks": []
            }),
            "streamSettings": json.dumps({
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "dest": "google.com:443",
                    "serverNames": ["google.com", "www.google.com"],
                    "privateKey": private_key,
                    "publicKey": public_key,
                    "shortIds": [short_id]
                },
                "tcpSettings": {
                    "header": {"type": "none"}
                }
            }),
            "sniffing": json.dumps({
                "enabled": True,
                "destOverride": ["http", "tls"]
            })
        }
        response = session.post(create_api_url, headers=self.headers, data=json.dumps(new_vless_key_data), verify=False)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(
                f"Error creating VLESS key: {response.status_code}, {response.text}")
        return response.json(), port, short_id

    def generate_vless_link(self, client_id, port, public_key, short_id, server_name="google.com"):
        return (f"vless://{client_id}@{self.server_ip}:{port}"
                f"?type=tcp&security=reality&pbk=&fp=firefox"
                f"&sni={server_name}&sid={short_id}&spx=%2F&flow=xtls-rprx-vision"
                f"#MASKNETVPN")

    def manage_vless_key(self, tg_id, username):
        with Session() as session:
            try:
                new_client = {
                    "id": self.generate_uuid(),
                    "flow": "xtls-rprx-vision",
                    "email": self.generate_uuid(),
                    "limitIp": 1,
                    "totalGB": 0,
                    "expiryTime": 0,
                    "enable": True,
                    "tgId": tg_id,
                    "remark": f"Пользователь: {username}, TgId: {tg_id}"
                }
                cert_data = self.get_certificate(session)
                response, port, short_id = self.create_vless_key(
                    session,
                    new_client,
                    cert_data["privateKey"],
                    cert_data["publicKey"]
                )
                key_id = response.get('obj', {}).get('id')
                vless_link = self.generate_vless_link(
                    client_id=new_client["id"],
                    port=port,
                    public_key=cert_data["publicKey"],
                    short_id=short_id,
                    server_name="google.com"
                )
                return vless_link, key_id
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")


class ShadowsocksKeyManager(BaseKeyManager):
    def create_shadowsocks_key(self, session, new_client, new_password, new_port):
        create_api_url = f"{self.base_url}/inbound/add"
        while True:
            new_ss_key_data = {
                "up": 0,
                "down": 0,
                "total": 0,
                "remark": new_client["remark"],
                "enable": True,
                "expiryTime": 0,
                "listen": "",
                "port": new_port,
                "protocol": "shadowsocks",
                "settings": json.dumps({
                    "method": "chacha20-ietf-poly1305",
                    "password": new_password,
                    "network": "tcp,udp",
                    "clients": [new_client]
                }),
                "streamSettings": json.dumps({
                    "network": "tcp",
                    "security": "none",
                    "tcpSettings": {
                        "header": {"type": "none"}
                    }
                }),
                "sniffing": json.dumps({
                    "enabled": True,
                    "destOverride": ["http", "tls"]
                })
            }
            response = session.post(create_api_url, headers=self.headers, data=json.dumps(new_ss_key_data),
                                    verify=False)
            if response.status_code == 200:
                response_data = response.json()
                response_data['password'] = new_password
                return response_data
            elif response.status_code == 400 and "port already in use" in response.text.lower():
                continue
            else:
                raise requests.exceptions.RequestException(
                    f"Error creating Shadowsocks key: {response.status_code}, {response.text}")

    def manage_shadowsocks_key(self, tg_id, username):
        with Session() as session:
            try:
                new_port = self.generate_port()
                new_password = uuid.uuid4().hex
                method = "chacha20-ietf-poly1305"
                new_client = {
                    "method": "chacha20-ietf-poly1305",
                    "password": new_password,
                    "email": self.generate_uuid(),
                    "limitIp": 1,
                    "totalGB": 0,
                    "expiryTime": 0,
                    "enable": True,
                    "tgId": tg_id,
                    "remark": f"Пользователь: {username}, TgId: {tg_id}"
                }
                response = self.create_shadowsocks_key(session, new_client, new_password, new_port)
                key_id = response.get('obj', {}).get('id')
                return self.generate_ss_link(new_port, new_password, method, key_id), key_id
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")

    def generate_ss_link(self, port, password, method, key_id):
        user_info = f"{method}:{password}".encode()
        user_info_base64 = base64.b64encode(user_info).decode()
        return f"ss://{user_info_base64}@{self.server_ip}:{port}?prefix=POST%20&type=tcp#MASKNETVPN - {key_id}"
