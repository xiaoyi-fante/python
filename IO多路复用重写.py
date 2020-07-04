import socket
import threading
import datetime
import logging
import selectors

FORMAT = "%(asctime)s %(threadName)s %(thread)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

class ChatServer:
    def __init__(self, ip='127.0.0.1', port=9999):
        self.sock = socket.socket()
        self.addr = (ip, port)

        self.event = threading.Event()
        self.selector = selectors.DefaultSelector()

    def start(self):
        self.sock.bind(self.addr)
        self.sock.listen()
        self.sock.setblocking(False)
        self.selector.register(self.sock, selectors.EVENT_READ, self.accept)

        threading.Thread(target=self.select, name='selector', daemon=True).start()

    def select(self):
        while not self.event.is_set():
            events = self.selector.select()
            print('-'*30)
            for key, mask in events:
                logging.info(key)
                logging.info(mask)
                callback = key.data
                callback(key.fileobj)

    def accept(self, sock:socket.socket):
        conn, raddr = sock.accept()
        conn.setblocking(False)
        self.selector.register(conn, selectors.EVENT_READ, self.recv)

    def recv(self, sock:socket.socket):
        data = sock.recv(1024)
        if not data or data == b'quit':
            self.selector.unregister(sock)
            sock.close()
            return
        msg = "{:%Y/%m/%d %H:%M:%S} {}:{}\n{}\n".format(datetime.datetime.now(), *sock.getpeername(), data.decode())
        logging.info(msg)
        msg = msg.encode()
        for key in self.selector.get_map().values():
            if key.data == self.recv:
                key.fileobj.send(msg)

    def stop(self):
        self.event.set()
        fobjs = []
        for fd, key in self.selector.get_map().items():
            fobjs.append(key.fileobj)
        for fobjs in fobjs:
            self.selector.unregister(fobjs)
            fobjs.close()
        self.selector.close()
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


