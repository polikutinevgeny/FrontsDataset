import pickle
from bulletin import Bulletin
from datetime import datetime

f = open('data.bin', 'rb')
r = pickle.load(f)
maxx = -10000
minx = 10000
maxy = -10000
miny = 10000
for i in r.keys():
    for j in r[i].fronts:
        try:
            for x, y in j[1]:
                maxx = max(maxx, x)
                minx = min(minx, x)
                maxy = max(maxy, y)
                miny = min(miny, y)
                if x > 90:
                    print(i, j)
        except Exception as e:
            print(e)
            print(i, j)
            exit()
print(maxx, minx, maxy, miny)
# print(sorted(r.keys()))
