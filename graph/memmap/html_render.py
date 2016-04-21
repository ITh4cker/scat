
import sys
from bs4 import BeautifulSoup
from random import randint

def generate_random_access(N):
    data = dict()
    A_MIN = 0
    A_MAX = 10000
    R_MIN = 0
    R_MAX = 100
    W_MIN = 0
    W_MAX = 100
    for i in xrange(N):
        addr = randint(A_MIN, A_MAX)
        while addr in data.keys():
            addr = randint(A_MIN, A_MAX)
        data[addr] = (randint(R_MIN, R_MAX), randint(W_MIN, W_MAX))
    return sorted([(a, r, w) for a, (r, w) in data.items()], key=lambda a:a[0])

def wc_l(fpath):
    with open(fpath, 'rb') as f:
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.read
        buf = read_f(buf_size)
        while buf:
            lines += buf.count(b'\n')
            buf = read_f(buf_size)
    return lines

def parse_access(fpath):
    print "[*] parsing data ..."
    data = list()
    DATA_SIZE = 1000000
    for i in xrange(DATA_SIZE):
        data.append(dict())
    LINES = wc_l(fpath)
    print LINES
    progress = 0.0
    with open(fpath, 'r') as f:
        for i, line in enumerate(f.readlines()):
            pg = round(((i * 100.0)/LINES)*10)/10
            if pg != progress:
                progress = pg
                print progress
            typ, val = line[:-1].split(":")
            val = int(val)
            if val not in data[val % DATA_SIZE].keys():
                data[val % DATA_SIZE][val] = [0,0]
            if typ == "p":
                data[val % DATA_SIZE][val][0] += 1
            else:
                data[val % DATA_SIZE][val][1] += 1
    to_sort = list()
    for d in data:
        for a, (r, w) in d.items():
            to_sort.append((a, r, w))
    return sorted(to_sort, key=lambda a:a[0])

def render(data):
    print "[*] rendering memory map ..."
    WINDOW_SIZE = 16000
    # di_max, i_max = max(enumerate([d[1] + d[2] for d in data]), key=lambda a: a[1])
    # D_MIN = max(di_max - WINDOW_SIZE/2, 0)
    # D_MAX = min(D_MIN + WINDOW_SIZE, len(data) - 1)
    senti = 0
    WDW = data[-1][0] - data[0][0]
    n = 0
    # Search for max density area
    senti_low = 0
    senti_high = 0
    while data[senti_high][0] - data[senti_low][0] < WINDOW_SIZE:
        senti_high += 1
    nmax = senti_high - senti_low
    n = nmax
    while senti_high < len(data) - 1:
        senti_high += 1
        n += 1
        while data[senti_high][0] - data[senti_low][0] > WINDOW_SIZE:
            senti_low += 1
            n -= 1
        if n > nmax:
            nmax = n
            senti_low_best = senti_low
    D_MIN = senti_low_best
    D_MAX = senti_low_best + nmax 
    a_min = data[D_MIN][0]
    a_max = data[D_MAX][0]
    print D_MIN, D_MAX
    print a_min, a_max
    print data[D_MIN:D_MAX]
    i_min = min([d[1] + d[2] for d in data[D_MIN:D_MAX]])
    i_max = max([d[1] + d[2] for d in data[D_MIN:D_MAX]])
    r_min = min([d[1] for d in data[D_MIN:D_MAX]])
    r_max = max([d[1] for d in data[D_MIN:D_MAX]])
    w_min = min([d[2] for d in data[D_MIN:D_MAX]])
    w_max = max([d[2] for d in data[D_MIN:D_MAX]])
    print i_min, i_max
    print r_min, r_max
    print w_min, w_max
    I_LEVEL = 6
    html = ""
    WIDTH = 16
    senti = D_MIN
    a_min = a_min - (a_min % WIDTH)
    for i in xrange(a_min, a_max + 1):
        if i % 100 == 0:
            print i
        if data[senti][0] == i:
            d = data[senti]
            senti += 1
        else:
            d = (i, 0, 0)
        if i % WIDTH == 0:
            html += "<tr>"
            html += "<td class=\"hdr-addr\">{0:06x}</td>".format(i)
        html += "<td data-addr={0} data-intensity={1} data-read={2} data-write={3}></td>\n".format(d[0], ((-i_min + d[1] + d[2]) * I_LEVEL) / i_max, d[1], d[2])
        if i % WIDTH == WIDTH - 1:
            html += "</tr>"
    if i % WIDTH != WIDTH - 1:
        html += "</tr>"
    return html


with open("template.html", "r") as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

memap = soup.select("#memory-map > tbody")[0]
data_content = BeautifulSoup(render(parse_access(sys.argv[1]))) #generate_random_access(1000)))
memap.append(data_content)

with open("mem_map.html", "w") as f:
    f.write(soup.prettify())

