import asyncio
import base64
import re

from database.context_manager import DatabaseContextManager
from logger.logging_config import logger
from outline_vpn.outline_vpn import OutlineVPN


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

