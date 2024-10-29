import requests
import json
import uuid
import random
import urllib3
import base64
from requests.sessions import Session

class ShadowsocksKeyManager:
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
            "Referer": f"https://{server_ip}:54321/mysecreturl/panel/inbounds",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.base_url = f"https://{server_ip}:54321/mysecreturl/panel"

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def generate_password(self):
        return uuid.uuid4().hex

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
            raise requests.exceptions.RequestException(f"Error fetching inbounds: {response.status_code}, {response.text}")

    def create_shadowsocks_key(self, session, new_client):
        create_api_url = f"{self.base_url}/inbound/add"
        while True:
            new_port = self.generate_port()
            new_password = self.generate_password()
            new_ss_key_data = {
                "up": 0,
                "down": 0,
                "total": 0,
                "remark": "",
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
                    "externalProxy": [],
                    "tcpSettings": {
                        "acceptProxyProtocol": False,
                        "header": {
                            "type": "none"
                        }
                    }
                }),
                "sniffing": json.dumps({
                    "enabled": True,
                    "destOverride": [
                        "http",
                        "tls",
                        "quic",
                        "fakedns"
                    ]
                })
            }
            response = session.post(create_api_url, headers=self.headers, data=json.dumps(new_ss_key_data), verify=False)
            if response.status_code == 200:
                response_data = response.json()
                response_data['password'] = new_password  # Add password to response data for generating ss link
                return response_data
            elif response.status_code == 400 and "port already in use" in response.text.lower():
                # Retry with a different port if the port is already in use
                continue
            else:
                raise requests.exceptions.RequestException(f"Error creating Shadowsocks key: {response.status_code}, {response.text}")


    def delete_shadowsocks_key(self, key_id):
        with Session() as session:
            try:
                delete_api_url = f"{self.base_url}/inbound/del/{key_id}"
                response = session.post(delete_api_url, headers=self.headers, verify=False)
                if response.status_code == 200:
                    print(f"Shadowsocks ключ с ID {key_id} успешно удален.")
                else:
                    raise requests.exceptions.RequestException(
                        f"Error deleting Shadowsocks key: {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Произошла ошибка при выполнении запроса: {e}")
            except ValueError as e:
                print(e)


    def update_shadowsocks_key(self, key_id, status: bool):
        with Session() as session:
            try:
                update_api_url = f"{self.base_url}/inbound/update/{key_id}"
                update_data = {
                    "id": key_id,
                    "enable": status
                }
                response = session.post(update_api_url, headers=self.headers, data=json.dumps(update_data), verify=False)
                if response.status_code == 200:
                    print(f"Shadowsocks ключ с ID {key_id} успешно обновлен")
                else:
                    raise requests.exceptions.RequestException(
                        f"Error updating Shadowsocks key: {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Произошла ошибка при выполнении запроса: {e}")
            except ValueError as e:
                print(e)

    def generate_ss_link(self, server_ip, port, password, method, key_id):
        user_info = f"{method}:{password}".encode()
        user_info_base64 = base64.b64encode(user_info).decode()
        return f"ss://{user_info_base64}@{server_ip}:{port}?prefix=POST%20&type=tcp#MASKNETVPN - {key_id}"

    def manage_shadowsocks_key(self):
        with Session() as session:
            try:
                # Создание нового Shadowsocks ключа
                new_client_id = self.generate_uuid()
                new_email = str(new_client_id)
                password = self.generate_password()
                new_client = {
                    "method": "chacha20-ietf-poly1305",
                    "password": password,
                    "email": new_email,
                    "limitIp": 1,
                    "totalGB": 0,
                    "expiryTime": 0,
                    "enable": True,
                    "tgId": "",
                    "subId": new_client_id,
                    "reset": 0
                }

                response = self.create_shadowsocks_key(session, new_client)
                key_id = response.get('obj', {}).get('id')
                print("Данные ключа:", response)
                port = response.get('obj', {}).get('port')
                method = new_client['method']
                ss_link = self.generate_ss_link(self.server_ip, port, password, method, key_id)
                print("SS ссылка:", ss_link)

            except requests.exceptions.RequestException as e:
                print(f"Произошла ошибка при выполнении запроса: {e}")


# Использование
if __name__ == "__main__":
    server_ip = "150.241.94.108"
    session_cookie = "MTcyOTk3Nzk4MHxEWDhFQVFMX2dBQUJFQUVRQUFCMV80QUFBUVp6ZEhKcGJtY01EQUFLVEU5SFNVNWZWVk5GVWhoNExYVnBMMlJoZEdGaVlYTmxMMjF2WkdWc0xsVnpaWExfZ1FNQkFRUlZjMlZ5QWYtQ0FBRUVBUUpKWkFFRUFBRUlWWE5sY201aGJXVUJEQUFCQ0ZCaGMzTjNiM0prQVF3QUFRdE1iMmRwYmxObFkzSmxkQUVNQUFBQUZQLUNFUUVDQVFWaFpHMXBiZ0VGWVdSdGFXNEF81ejr2lRCWJZc8IAFDWdX-R9wrwfVe3ri3QR_lYf2D90="
    manager = ShadowsocksKeyManager(server_ip, session_cookie)
    manager.manage_shadowsocks_key()
