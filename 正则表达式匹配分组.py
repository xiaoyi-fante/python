import re

s = '''bottle\nbag\nbig\napple'''

for i,c in enumerate(s,1):
    print((i-1,c),end='\n' if i%8==0 else ' ')
print()

regex = re.compile('(b\w+)')
result = regex.match(s)
print(type(result))
print(1, 'match', result.groups())

result = regex.search(s,1)
print(2, 'search', result.groups())


regex = re.compile('(b\w+)\n(?P<name2>b\w+)\n(?P<name3>b\w+)')
result = regex.match(s)
print(3, 'match', result)
print(4, result.group(3), result.group(2), result.group(1))
print(5, result.group(0).encode())
print(6, result.group('name2'), result.group('name3'))
print(6, result.groups())

print(7, result.groupdict())

result = regex.findall(s)
for x in result:
    print(type(x), x)

regex = re.compile('(?P<head>b\w+)')
result = regex.finditer(s)
for x in result:
    print(type(x), x, x.group(), x.group('head'))