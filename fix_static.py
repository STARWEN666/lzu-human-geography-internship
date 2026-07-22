import json, re
from urllib.parse import quote

html = open('index.html', encoding='utf-8').read()

# --- 1. Parse POINTS array (single line) ---
start = html.index('const POINTS = ') + len('const POINTS = ')
end = html.index(']\nconst ROUTE_DAYS', start) + 1
pts = json.loads(html[start:end])

print('POINTS count =', len(pts))
print('POINTS order ids:')
for p in pts:
    print('  ', p['day'], p['id'], '|', p['name'])

# --- 2. Build table rows ---
def row(p, num):
    pid, name, area, ptype, task, day = p['id'], p['name'], p['area'], p['type'], p['task'], p['day']
    city = area.split('·')[0]
    kw = quote(name); city_enc = quote(city)
    return (f'<tr data-day="{day}">\n'
            f'<td>{num}</td>'
            f'<td><button class="plain-btn" onclick="openDetail(\'{pid}\')">{name}</button></td>'
            f'<td>{area}</td><td>{ptype}</td><td>{task}</td>'
            f'<td><a href="https://uri.amap.com/search?keyword={kw}&amp;city={city_enc}&amp;callnative=1" target="_blank">高德导航</a></td>\n'
            f'</tr>')

new_tbody = '<tbody>\n' + '\n'.join(row(p, i+1) for i, p in enumerate(pts)) + '\n</tbody>'

# --- 3. Build detail cards ---
def card(p):
    pid, day, name, area, ptype, part = p['id'], p['day'], p['name'], p['area'], p['type'], p['part']
    img, intro, observe, task, output = p['img'], p['intro'], p['observe'], p['task'], p['output']
    hours = p.get('hours', '')
    lon, lat = p['lon'], p['lat']
    name_enc = quote(name)
    hours_p = f'<p><strong>开放安排：</strong>{hours}</p>' if hours else ''
    return (f'<article class="detail-card" data-day="{day}" id="card-{pid}">\n'
            f'<img alt="{name}" loading="lazy" onerror="this.onerror=null;this.src=\'https://placehold.co/1200x720/e7efe3/24412d?text={name}\'" src="{img}"/>\n'
            f'<div class="detail-body">\n'
            f'<div class="tag">{day} · {part} · {ptype}</div>\n'
            f'<h3>{name}</h3>\n'
            f'<p><strong>点位介绍：</strong>{intro}</p>\n'
            f'<p><strong>观察重点：</strong>{observe}</p>\n'
            f'<p><strong>现场任务：</strong>{task}</p>\n'
            f'{hours_p}'
            f'<p><strong>建议产出：</strong>{output}</p>\n'
            f'<div class="link-row"><a class="mini-link" href="https://uri.amap.com/marker?position={lon},{lat}&amp;name={name_enc}&amp;coordinate=gaode&amp;callnative=1" rel="noopener" target="_blank">打开高德导航</a>'
            f'<button class="mini-link btn-like" onclick="focusPoint(\'{pid}\')">地图定位</button></div>\n'
            f'</div>\n'
            f'</article>')

new_grid = '<div class="detail-grid">\n' + '\n'.join(card(p) for p in pts) + '\n</div>'

# --- 4. Apply replacements ---
old_tbody_m = re.search(r'<tbody>[\s\S]*?</tbody>', html)
old_grid_m = re.search(r'<div class="detail-grid">[\s\S]*?</article></div>', html)
print('\ntbody match:', bool(old_tbody_m))
print('grid match:', bool(old_grid_m))

html2 = html[:old_tbody_m.start()] + new_tbody + html[old_tbody_m.end():]
grid_m2 = re.search(r'<div class="detail-grid">[\s\S]*?</article></div>', html2)
html2 = html2[:grid_m2.start()] + new_grid + html2[grid_m2.end():]

open('index.html', 'w', encoding='utf-8').write(html2)
print('\nWROTE index.html, new length =', len(html2))
