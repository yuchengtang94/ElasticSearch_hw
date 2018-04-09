import re

str = 'test random'

s = re.findall('\"(.*?)\"', str)

print(s)