import json, re, subprocess
from urllib.parse import quote

cur = open('index.html', encoding='utf-8').read()
head = subprocess.check_output(['git', 'show', 'HEAD:index.html']).decode('utf-8')

# --- parse POINTS from cur ---
start = cur.index('const POINTS = ') + len('const POINTS = ')
end = cur.index(']\nconst ROUTE_DAYS', start) + 1
pts = json.loads(cur[start:end])
assert len(pts) == 25, f'POINTS count = {len(pts)}'

def row(p, num):
    pid, name, area, ptype, task, day = p['id'], p['name'], p['area'], p['type'], p['task'], p['day']
    city = area.split('·')[0]
    kw = quote(name); city_enc = quote(city)
    return (f'<tr data-day="{day}">\n<td>{num}</td>'
            f'<td><button class="plain-btn" onclick="openDetail(\'{pid}\')">{name}</button></td>'
            f'<td>{area}</td><td>{ptype}</td><td>{task}</td>'
            f'<td><a href="https://uri.amap.com/search?keyword={kw}&amp;city={city_enc}&amp;callnative=1" target="_blank">高德导航</a></td>\n</tr>')

new_tbody = '<tbody>\n' + '\n'.join(row(p, i + 1) for i, p in enumerate(pts)) + '\n</tbody>'

# --- 1. restore schedule tbody from HEAD ---
hsm = re.search(r'(<section class="section" id="schedule">[\s\S]*?)(<tbody>[\s\S]*?</tbody>)', head)
assert hsm, 'head schedule tbody not found'
head_sched = hsm.group(2)
csm = re.search(r'(<section class="section" id="schedule">[\s\S]*?)(<tbody>[\s\S]*?</tbody>)', cur)
cur = cur[:csm.start(2)] + head_sched + cur[csm.end(2):]

# --- 2. replace points tbody with new_tbody ---
cpm = re.search(r'(<section class="section" id="points">[\s\S]*?)(<tbody>[\s\S]*?</tbody>)', cur)
assert cpm, 'points tbody not found'
cur = cur[:cpm.start(2)] + new_tbody + cur[cpm.end(2):]

open('index.html', 'w', encoding='utf-8').write(cur)
print('done. len=', len(cur))
