import selectors
import threading
import socket
import logging

FORMAT = "%(asctime)s %(threadName)s %(thread)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

def accept(sock:socket.socket, mask):
    conn, raddr = sock.accept()
    conn.setblocking(False)
    key = selector.register(conn, selectors.EVENT_READ, read)
    logging.info(key)

def read(conn:socket.socket, mask):
    data = conn.recv(1024)
    msg = "Your msg is {}.".format(data.decode())
    conn.send(msg.encode())

selector = selectors.DefaultSelector()

sock = socket.socket()
sock.bind(('0.0.0.0', 9999))
sock.listen()
logging.info(sock)

sock.setblocking(False)

key = selector.register(sock, selectors.EVENT_READ, accept)
logging.info(key)

e = threading.Event()

def select(e):
    while not e.is_set():
        events = selector.select()
        print('-'*30)
        for key, mask in events:
            logging.info(key)
            logging.info(mask)
            callback = key.data
            callback(key.fileobj, mask)

threading.Thread(target=select, args=(e,), name='select').start()

def main():
    while not e.is_set():
        cmd = input('>>')
        if cmd.strip() == 'quit':
            e.set()
            fobjs = []
            logging.info('{}'.format(list(selector.get_map().items())))

            for fd, key in selector.get_map().items():
                print(fd, key)
                print(key.fileobj)
                fobjs.append(key.fileobj)

            for fobjs in fobjs:
                selector.unregister(fobjs)
                fobjs.close()
            selector.close()
if __name__ == '__main__':
    main()