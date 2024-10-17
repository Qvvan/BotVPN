import asyncio
import base64
import re

from outline_vpn.outline_vpn import OutlineVPN

from telegram_bot.database.context_manager import DatabaseContextManager
from telegram_bot.logger.logging_config import logger


class OutlineManager:
    def __init__(self):
        self.clients = {}
        self.initialization_done = asyncio.Event()
        asyncio.create_task(self.initialize_clients())

    async def initialize_clients(self):
        async with DatabaseContextManager() as session_methods:
            try:
                servers = await session_methods.servers.get_all_servers()

                for server in servers:
                    self.clients[server.server_id] = OutlineVPN(
                        api_url=server.api_url,
                        cert_sha256=server.cert_sha256
                    )

                if self.clients:
                    logger.info(f"Initialized {len(self.clients)} servers.")
                else:
                    logger.warning("No servers found in the database.")

                self.initialization_done.set()

            except Exception as e:
                logger.error(f"Error initializing clients: {e}")

    async def wait_for_initialization(self):
        await self.initialization_done.wait()

    async def list_servers(self):
        server_info = {}
        for server_id, client in self.clients.items():
            try:
                info = client.get_server_information()
                server_info[server_id] = info['name']
            except Exception as e:
                logger.error(f"Error fetching information for web {server_id}: {e}")
                server_info[server_id] = f"Ошибка: {str(e)}"
        return server_info

    async def get_server_id_by_name(self, server_name: str):
        servers = await self.list_servers()
        for server_id, name in servers.items():
            if name == server_name:
                return server_id
        return None

    async def create_key(self, server_id: str, user_id: str):
        if server_id in self.clients:
            return self.clients[server_id].create_key(name='Свободый', key_id=user_id)
        raise ValueError(f"Server ID {server_id} not found.")

    async def delete_key(self, server_id: str, key_id: str):
        if server_id in self.clients:
            return self.clients[server_id].delete_key(key_id)
        raise ValueError(f"Server ID {server_id} not found.")

    async def rename_key(self, server_id: str, key_id: str, new_key_name: str):
        if server_id in self.clients:
            return self.clients[server_id].rename_key(key_id, new_key_name)
        raise ValueError(f"Server ID {server_id} not found.")

    async def delete_limit(self, server_id: str, key_id: str):
        if server_id in self.clients:
            return self.clients[server_id].delete_data_limit(key_id)
        raise ValueError(f"Server ID {server_id} not found.")

    async def upd_limit(self, server_id: str, key_id: str):
        if server_id in self.clients:
            return self.clients[server_id].add_data_limit(key_id, 0)
        raise ValueError(f"Server ID {server_id} not found.")

    async def decrypt_key(self, key: str) -> dict:
        match = re.search(r'@(.*?):(\d+)', key)
        if not match:
            raise ValueError("Unable to extract web and port")

        server = match.group(1)
        server_port = int(match.group(2))

        encoded_part = key.split("ss://")[1].split('@')[0]

        decoded_part = base64.b64decode(encoded_part).decode('utf-8')

        method, password = decoded_part.split(':', 1)

        return {
            "web": server,
            "server_port": server_port,
            "password": password,
            "method": method,
        }
