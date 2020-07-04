import socket
import threading
import datetime
import logging

FORMAT = "%(asctime)s %(threadName)s %(thread)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

class ChatUDPServer:
    def __init__(self, ip='127.0.0.1', port=9993, interval=10):
        self.addr = (ip, port)
        self.sock = socket.socket(type=socket.SOCK_DGRAM)
        self.clients = {}
        self.event = threading.Event()
        self.interval = interval

    def start(self):
        self.sock.bind(self.addr)
        threading.Thread(target=self.recv, name='recv').start()

    def recv(self):
        while not self.event.is_set():
            localset = set()
            data, raddr = self.sock.recvfrom(1024)

            current = datetime.datetime.now().timestamp()
            if data.strip() == b'^hb^':
                print('^^^^^^^^hb', raddr)
                self.clients[raddr] = current
                continue
            elif data.strip() == b'quit':
                self.clients.pop(raddr, None)
                logging.info('{} leaving'.format(raddr))
                continue

            self.clients[raddr] = current

            msg = '{}. from {}:{}'.format(data.decode(), *raddr)
            logging.info(msg)
            msg = msg.encode()

            for c, stamp in self.clients.items():
                if current - stamp > self.interval:
                    localset.add(c)
                else:
                    self.sock.sendto(msg, c)
            for c in localset:
                self.clients.pop(c)

    def stop(self):
        for c in self.clients:
            self.sock.sendto(b'bye', c)
        self.sock.close()
        self.event.set()

def main():
    cs = ChatUDPServer()
    cs.start()

    while True:
        cmd = input(">>>")
        if cmd.strip() == 'quit':
            cs.stop()
            break
        logging.info(threading.enumerate())
        logging.info(cs.clients)

if __name__ == '__main__':
    main()


# =================使用ThreadingTCPServer改写==========================

import threading
from socketserver import ThreadingTCPServer, BaseRequestHandler
import sys
import logging

FORMAT = "%(asctime)s %(threadName)s %(thread)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

class ChatHandler(BaseRequestHandler):
    clients = {}

    def setup(self):
        super().setup()
        self.event = threading.Event()
        self.clients[self.client_address] = self.request

    def finish(self):
        super().finish()
        self.clients.pop(self.client_address)
        self.event.set()

    def handle(self):
        super().handle()
        while not self.event.is_set():
            data = self.request.recv(1024).decode()
            if data == 'quit':
                break
            msg = "{} {}".format(self.client_address, data).encode()
            logging.info(msg)
            for c in self.clients.values():
                self.request.send(msg)
        print('End')

addr = ('0.0.0.0', 9979)
server = ThreadingTCPServer(addr, ChatHandler)

server_thread = threading.Thread(target=server.serve_forever, name='CharServer', daemon=True)
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