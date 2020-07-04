import random
import datetime
import time
from queue import Queue
import threading
import re
from pathlib import Path

# PATTERN='''(?P<remote>[\d\.]{7,})\s-\s-\s\[(?P<datetime>[^\[\]]+)\]\s\
# "(?P<method>.*)\s(?P<url>.*)\s(?P<protocol>.*)"\s\
# (?P<status>\d{3})\s(?P<size>\d+)\s"[^"]+"\s"(?P<useragent>[^"]+)"'''

PATTERN = '''(?P<remote>[\d\.]{7.}) - - \[(?P<datetime>[^\[\]]+)\] "(?P<request>[^"]+)" \
(?P<status>\d+) (?P<size>\d+) "[^"]+" "(?P<useragent>[^"]+)"'''

regex = re.compile(PATTERN)

from user_agents import parse
ops = {
    'datetime': lambda datestr: datetime.datetime.strptime(datestr, '%d/%b/%Y:%H:%M:%S %z'),
    'status': int,
    'size': int,
    'request': lambda request:dict(zip(('method', 'url', 'protocol'), request.split()))
}

def extract(line:str) -> dict:
    matcher = regex.match(line)
    if matcher:
        return {name:ops.get(name, lambda x:x)(data) for name,data in matcher.groupdict().items()}

def openfile(path:str):
    with open(path) as f:
        for line in f:
            fields = extract(line)
            if fields:
                yield fields
            else:
                continue

def load(*paths):
    for item in paths:
        p = Path(item)
        if not p.exists():
            continue
        if p.is_dir():
            for file in p.iterdir():
                if file.is_file():
                    yield from openfile(str(file))
        elif p.is_file():
            yield from openfile(str(p))

def source(second=1):
    while True:
        yield {
            'datetime': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))),
            'value': random.randint(1,100)
        }
        time.sleep(second)

def window(src:Queue, handler, width:int, interval:int):
    """
    窗口函数

    :param src: 数据源，缓存队列，用来拿数据
    :param handler: 数据处理函数
    :param width: 时间窗口宽度，秒
    :param interval: 处理时间间隔，秒
    :return: None
    """

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
            print('{}'.format(ret))
            start = current
            buffer = [x for x in buffer if x['datetime'] > current-delta]

def handler(iterable):
    return sum(map(lambda x:x['value'], iterable)) / len(iterable)

def donothing_handler(iterable):
    return iterable

def status_handler(iterable):
    status = {}
    for item in iterable:
        key = item['status']
        status[key] = status.get(key, 0) + 1
    total = len(iterable)
    return {k:status[k]/total for k,v in status.items()}

allbrowsers = {}

def browser_handler(iterable):
    browsers = {}
    for item in iterable:
        ua = item['useragent']

        key = (ua.browser.family, ua.browser.version_string)
        browsers[key] = browsers.get(key, 0) + 1
        allbrowsers[key] = allbrowsers.get(key,0) + 1

    print(sorted(allbrowsers.items(), key=lambda x:x[1], reverse=True)[:10])
    return browsers

def dispatcher(src):
    handlers = []
    queues = []

    def reg(handler, width:int, interval:int):
        """
        注册 窗口处理函数

        :param handler: 注册的数据处理函数
        :param width: 时间窗口宽度
        :param interval: 时间间隔
        :return: None
        """
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

# if __name__ == "__main__":
#     import sys
#     path = 'test.log'
#     reg, run = dispatcher(load(path))
#     reg(status_handler, 10, 5)
#     reg(browser_handler, 5, 5)
#     run()

reg, run = dispatcher(load('test.log'))
reg(status_handler, 10, 5)
run()
