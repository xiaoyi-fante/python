from collections import defaultdict
import re

def makekey2(line:str, chars=set("""!'"#./\()[],*-\r\n""")):
    start = 0
    for i, c in enumerate(line):
        if c in chars:
            if start == i:
                start += 1
                continue
            yield line[start:i]
            start = i + 1
    else:
        if start < len(line):
            yield line[start:]

regex = re.compile('[^\w-]+')

def makekey3(line:str):
    for word in regex.split(line):
        if len(word):
            yield word

def wordcount(filename, encoding='utf-8', ignore=set()):
    d = defaultdict(lambda :0)
    with open(filename, encoding=encoding) as f:
        for line in f:
            for word in map(str.lower, makekey2(line)):
                if word not in ignore:
                    d[word] += 1
    return d

def top(d:dict, n=10):
    for i, (k, v) in enumerate(sorted(d.items(), key=lambda item: item[1], reverse=True)):
        if i > n:
            break
        print(k,v)

top(wordcount('sample', ignore={'video'}))

