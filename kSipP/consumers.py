import asyncio
import os, signal, psutil
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
import json, socket

class SippLogConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        query_params = parse_qs(self.scope["query_string"].decode())
        self.xml = query_params.get("xml")[0]
        self.pid = query_params.get("pid")[0]
        self.cport = query_params.get("cp")[0]
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
            # inial reading screen to avoid delay
            with open(self.log_file_path, 'r') as f:
                content = f.read()
            await self.send(text_data=content)
            await asyncio.sleep(0.8)
            
            while self.running:
                try:
                    proc = psutil.Process(int(self.pid))
                    if not proc.is_running() or proc.status() == psutil.STATUS_ZOMBIE:
                        await self.send(text_data="[INFO] SIPp process has exited.")
                        try:
                            proc.wait(timeout=1)  # Reap if it's a zombie
                        except psutil.TimeoutExpired:
                            pass
                        self.running = False
                        break

                except psutil.NoSuchProcess:
                    await self.send(text_data="[INFO] SIPp process has exited.")
                    self.running = False
                    break

                os.kill(int(self.pid), signal.SIGUSR2)
                await asyncio.sleep(1)
                with open(self.log_file_path, 'r') as f:
                    content = f.read()
                await self.send(text_data=content)

        except Exception as e:
            await self.send(text_data=f"[ERROR] Could not read screen log: {str(e)}")


    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "send_signal":
                key = data.get("key", "")
                udp_ip = "127.0.0.1"
                udp_port = int(self.cport)  # Define this per connection/session

                if key == "kill":
                    try:
                        process = psutil.Process(int(self.pid))
                        process.terminate()  # You can also use process.kill() for a more forceful termination
                        process.wait(timeout=2)  # Wait for it to exit
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        pass  # The process with the given PID doesn't exist or already terminated

                elif key:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto(key.encode(), (udp_ip, udp_port))
                        sock.close()
                        await self.send(text_data=f"Sent key '{key}' to SIPp on port {udp_port}")
                    except Exception as e:
                        await self.send(text_data=f"[ERROR] Sending UDP: {str(e)}")
                else:
                    await self.send(text_data="[ERROR] No key provided")

            else:
                await self.send(text_data="[ERROR] Unknown action")


        except Exception as e:
            await self.send(text_data=f"[ERROR] {str(e)}")