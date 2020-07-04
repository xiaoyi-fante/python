import socket
import threading
import datetime
import logging

FORMAT = "%(asctime)s %(threadName)s %(thread)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

class ChatClient:
    def __init__(self, ip='127.0.0.1', port=9995):
        self.sock = socket.socket()
        self.addr = (ip, port)
        self.event = threading.Event()

    def start(self):
        self.sock.connect(self.addr)
        self.send("I'm ready.")
        threading.Thread(target=self.recv, name='recv').start()

    def recv(self):
        while not self.event.is_set():
            try:
                data = self.sock.recv(1024)
            except Exception as e:
                logging.error(e)
                break
            msg = "{:%Y/%m/%d %H:%M:%S} {}:{}\n{}\n".format(datetime.datetime.now(), *self.addr, data.strip())
            logging.info(msg)

    def send(self, msg:str):
        data = "{}\n".format(msg.strip()).encode()
        self.sock.send(data)

    def stop(self):
        self.sock.close()
        self.event.wait(3)
        self.event.set()
        logging.info('Client stops.')

def main():
    cc = ChatClient()
    cc.start()
    while True:
        cmd = input('>>>')
        if cmd.strip() == 'quit':
            cc.stop()
            break
        cc.send(cmd)
if __name__ == '__main__':
    main()