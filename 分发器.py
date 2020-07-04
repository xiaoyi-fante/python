import random
import datetime
import time
from queue import Queue
import threading

def source(second=1):
    while True:
        yield {
            'datetime': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))),
            'value': random.randint(1,100)
        }
        time.sleep(second)

def window(src:Queue, handler, width:int, interval:int):
    start = datetime.datetime.strptime('20170101 000000 +0800', '%Y%m%d %H%M%S %z')
    current = datetime.datetime.strptime('20170101 010000 +0800', '%Y%m%d %H%M%S %z')

    buffer = []
    delta = datetime.timedelta(seconds=width-interval)

    while True:
        data = src.get()
        if data:
            buffer.append(data)
            current = data['datetime']
        if (current-start).total_seconds() >= interval:
            ret = handler(buffer)
            print('{:.2f}'.format(ret))
            start = current

            buffer = [x for x in buffer if x['datetime'] > current - delta]

def handler(iterable):
    return sum(map(lambda x:x['value'], iterable)) / len(iterable)

def dispatcher(src):
    handlers = []
    queues = []

    def reg(handler, width:int, interval:int):
        q = Queue()
        queues.append(q)

        h = threading.Thread(target=window, args=(q, handler, width, interval))
        handlers.append(h)

    def run():
        for t in handlers:
            t.start()

        for item in src:
            for q in queues:
                q.put(item)
    return reg, run

reg,run = dispatcher(source())

reg(handler, 10, 5)
run()