import random
import datetime
import time

def source(second=1):
    while True:
        yield {
            'datetime': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))),
            'value': random.randint(1,100)
        }
        time.sleep(second)

def window(iterator, handler, width:int, interval:int):
    start = datetime.datetime.strptime('20170101 000000 +0800', '%Y%m%d %H%M%S %z')
    current = datetime.datetime.strptime('20170101 010000 +0800', '%Y%m%d %H%M%S %z')

    buffer = []
    delta = datetime.timedelta(seconds=width-interval)

    while True:
        data = next(iterator)
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

window(source(),handler,10,5)