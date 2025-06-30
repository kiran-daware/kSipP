import asyncio
import os, signal
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

class SippLogConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        query_params = parse_qs(self.scope["query_string"].decode())
        self.xml = query_params.get("xml", ["uas_basic"])[0]
        self.pid = query_params.get("pid", ["12345"])[0]
        self.running = True

        self.log_file_path = f"/home/kiran/kgit/kSipP/{self.xml}_{self.pid}_screen.log"
        self.stream_task = asyncio.create_task(self.stream_logs())

        async def disconnect(self, close_code):
            self.running = False
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass

    async def stream_logs(self):
        try:
            while self.running:
                os.kill(int(self.pid), signal.SIGUSR2)
                await asyncio.sleep(1)
                print(self.pid)
                with open(self.log_file_path, 'r') as f:
                    content = f.read()
                await self.send(text_data=content)
                await asyncio.sleep(1)
        except Exception as e:
            await self.send(text_data=f"[ERROR] Could not read screen log: {str(e)}")
