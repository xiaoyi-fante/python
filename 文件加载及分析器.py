import datetime
import re
from queue import Queue
import threading
from pathlib import Path
import random

log = '123.125.71.36 - - [06/Apr/2017:18:08:25 +0800] "GET / HTTP/1.1" 200 8642 "-" "Mozilla/5.0 (compatible; Baiduspider/2.0; \
      +http://www.baidu.com/search/spider.html)"'
pattern = '''(?P<remote>[\d\.]{7,}) - - \[(?P<datetime>[^\[\]]+)\] "(?P<request>[^"]+)" \
(?P<status>\d+) (?P<size>\d+) "[^"]+" "(?P<useragent>[^"]+)"'''

regex = re.compile(pattern)

def extract(line):
    matcher = regex.match(line)
    if matcher:
        return {k:ops.get(k, lambda x:x)(v) for k,v in matcher.groupdict().items()}

ops = {
    'datetime': lambda timestr:datetime.datetime.strptime(timestr, "%d\%b\%Y:%H:%M:%S %z"),
    'status': int,
    'size': int,
    'request': lambda request:dict(zip(('method','url','protocol'), request.splist()))
}

def openfile(path:str):
    with open(path) as f:
        for line in f:
            fields = extract(line)
            if fields:
                yield fields
            else:
                continue

def load(*path):
    for item in path:
        p = Path(item)
        if not p.exists():
            continue
        if p.is_dir():
            for file in p.iterdir():
                if file.is_file():
                    yield from openfile(str(file))
        elif p.is_file():
            yield from openfile(str(p))

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

def donothing_handler(iterable:list):
    return iterable

def status_handler(iterable):
    status = {}
    for item in iterable:
        key = item['status']
        status[key] = status.get(key, 0) + 1
    total = len(iterable)
    return {k:status[k]/total for k,v in status.items()}

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

reg,run = dispatcher(load('test.log'))

reg(handler, 10, 5)
run()
