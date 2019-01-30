import re
from datetime import datetime, timezone

import dateutil
from dateutil import parser

import jsonpickle
import requests
import requests_cache
from bulletin import Bulletin

requests_cache.install_cache('data_cache')

tzinfos_us = {
    'PST': dateutil.tz.gettz('US/Pacific'),
    'PDT': dateutil.tz.gettz('US/Pacific'),
    'PT': dateutil.tz.gettz('US/Pacific'),
    'MST': dateutil.tz.gettz('US/Mountain'),
    'MDT': dateutil.tz.gettz('US/Mountain'),
    'MT': dateutil.tz.gettz('US/Mountain'),
    'CST': dateutil.tz.gettz('US/Central'),
    'CDT': dateutil.tz.gettz('US/Central'),
    'CT': dateutil.tz.gettz('US/Central'),
    'EST': dateutil.tz.gettz('US/Eastern'),
    'EDT': dateutil.tz.gettz('US/Eastern'),
    'ET': dateutil.tz.gettz('US/Eastern')}

front_types = ('WARM', 'COLD', 'STNRY', 'OCFNT', 'TROF')
strength = ('WK', 'MDT', 'STG')
remove_newlines = re.compile(r'\n(\d)')
fronts = re.compile(
    '({})( ({}))? (.*)\n'.format('|'.join(front_types), '|'.join(strength)))
date_expr = re.compile(r'VALID (\d{6})')
bulletin_date_expr = re.compile(
    r'^\d{3,4} [AP]M [A-Z]{3} [A-Z]{3} [A-Z]{3} \d{2} \d{4}$', re.MULTILINE)
splitter = re.compile('\x01(.*?)\x03', re.DOTALL)
version = re.compile('ASUS1|ASUS01|ASUS02')


def parse_codsus(s, year):
    t = version.findall(s)[0]
    parse_front = parse_codsus_front if t == 'ASUS1' or t == 'ASUS01' else parse_codsus_hr_front

    def parse_fronts(x):
        return x[0], parse_front(x[3].split())

    d = edit_time(bulletin_date_expr.findall(s))
    s = remove_newlines.sub(r' \g<1>', s)
    date = date_expr.findall(s)[0]
    month, day, hour = map(int, (date[:2], date[2:4], date[4:6]))
    date = datetime(year, month, day, hour, tzinfo=timezone.utc)
    res = Bulletin(
        date,
        parser.parse(d, tzinfos=tzinfos_us) if d else parser.parse('19000101 00:00 UTC'),
        list(map(parse_fronts, fronts.findall(s))),
        'SR' if t == 'ASUS1' or t == 'ASUS01' else 'HR'
    )
    if not res.fronts:
        raise ValueError("No fronts in bulletin")
    return res


def edit_time(t):
    if not t:
        return None
    t = t[0]
    if t[3] == ' ':
        return t[0] + ':' + t[1:]
    else:
        return t[:2] + ':' + t[2:]


def parse_codsus_front(l):
    raise ValueError('Fuck CODSUS')
    # a = [(int(x[:2]), int(x[2:])) for x in l]
    # if any(x < 0 for x, _ in a):
    #     raise ValueError('Negative number in bulletin (see 2003-08-09 03:00:00)')
    # if any(x[0] == '0' for x in l):
    #     raise ValueError
    # return a


def parse_codsus_hr_front(l):
    return [(int(x[:3]) / 10, -int(x[3:]) / 10) for x in l]


def get_year(year):
    contents = requests.get(
        'https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?'
        'fmt=text&pil=CODSUS&center=&limit=17520&sdate={0}-01-01&edate={1}-12-31'
            .format(year, year)
    ).text
    print(year, 'downloaded')
    data = splitter.findall(contents)
    results = dict()
    process_data(data, results, year)
    url = 'https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?' \
          'fmt=text&pil=CODSUS&center=&limit=17520&sdate={0}-12-31&edate={1}-01-01'
    contents = requests.get(url.format(year, year + 1)).text
    data = splitter.findall(contents)
    process_data(data, results, year, lambda x: x.valid.month == 12)
    contents = requests.get(url.format(year - 1, year)).text
    data = splitter.findall(contents)
    process_data(data, results, year, lambda x: x.valid.month == 1)
    return results


def process_data(data, results, year, condition=None):
    for d in data:
        try:
            b = parse_codsus(d, year)
            if condition and not condition(b):
                continue
            if b.valid not in results or results[b.valid].issued < b.issued:
                results[b.valid] = b
        except:
            continue


r = dict()
for i in range(2000, 2019):
    d = get_year(i)
    r = {**r, **d}
    # f = open('data/{}.json'.format(i), 'w')
    # f.write(jsonpickle.encode(d))
    # f.close()
    print(i)
import pickle

f = open('data.bin', 'wb')
pickle.dump(r, f, pickle.HIGHEST_PROTOCOL)
print('Total:', len(r))

# print(len(d))
# for i in d.keys():
#     print(i.isoformat(' '))
# for i in list(d.values())[:10]:
#     print(i)
# contents = urllib \
#     .request \
#     .urlopen(
#     'https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?'
#     'fmt=text&pil=CODSUS&center=&limit=9999&sdate=2017-12-31&edate=2018-01-05') \
#     .read().decode('ascii')
# data = splitter.findall(contents)
# print(len(data))
# print(len(contents))
# for d in data:
#     parse_codsus(d)
