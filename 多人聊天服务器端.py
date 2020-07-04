import logging
import socket
import threading
import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(thread)d %(message)s")

class ChatServer:
    def __init__(self, ip='127.0.0.1', port=9995):
        self.sock = socket.socket()
        self.addr = (ip, port)
        self.clients = {}
        self.event = threading.Event()

    def start(self):
        self.sock.bind(self.addr)
        self.sock.listen()
        threading.Thread(target=self.accept).start()

    def accept(self):
        while not self.event.is_set():
            sock, client = self.sock.accept()
            f = sock.makefile('rw')
            self.clients[client] = f
            threading.Thread(target=self.recv, args=(f, client), name='recv').start()

    def recv(self, f, client):
        while not self.event.is_set():
            try:
                data = f.readline()
            except Exception as e:
                logging.error(e)
                data = 'quit'
            msg = data.strip()
            if msg == 'quit':
                self.clients.pop(client)
                f.close()
                logging.info('{} quits'.format(client))
                break
            msg = "{:%Y/%m/%d %H:%M:%S} {}:{}\n{}\n".format(datetime.datetime.now(), *client, data)
            logging.info(msg)
            for s in self.clients.values():
                s.write(msg)
                s.flush()

    def stop(self):
        for s in self.clients.values():
            s.close()
        self.sock.close()
        self.event.set()

def main():
    cs = ChatServer()
    cs.start()

    while True:
        cmd = input('>>').strip()
        if cmd == 'quit':
            cs.stop()
            threading.Event().wait(3)
            break
        logging.info(threading.enumerate())

if __name__ == '__main__':
    main()