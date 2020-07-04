import threading
from socketserver import ThreadingTCPServer, BaseRequestHandler
import logging
import sys

class EchoHandler(BaseRequestHandler):
    def setup(self):
        super().setup()
        self.event = threading.Event()

    def finish(self):
        super().finish()
        self.event.set()

    def handle(self):
        super().handle()

        while not self.event.is_set():
            data = self.request.recv(1024).decode()
            msg = "{} {}".format(self.client_address, data).encode()
            self.request.send(msg)
        print('End')

addr = ('0.0.0.0', 9989)
server = ThreadingTCPServer(addr, EchoHandler)

server_thread = threading.Thread(target=server.serve_forever, name='EchoServer', daemon=True)
server_thread.start()

try:
    while True:
        cmd = input('>>>')
        if cmd.strip() == 'quit':
            break
        print(threading.enumerate())
except Exception as e:
    print(e)
except KeyboardInterrupt:
    pass
finally:
    print('Exit')
    sys.exit(0)