from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old_css_start = '.status-guide-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:14px 0;border-bottom:1px solid var(--line)}'
old_css_end = '.status-guide-card.cost .status-guide-icon{color:#a9d9ff;background:rgba(98,182,255,.07);border-color:rgba(98,182,255,.2)}'
start = text.find(old_css_start)
end = text.find(old_css_end)
if start < 0 or end < 0 or end < start:
    raise SystemExit('status guide CSS block not found')
end += len(old_css_end)
new_css = '.status-guide-list{padding:8px 0 14px;border-bottom:1px solid var(--line)}.status-guide-row{display:grid;grid-template-columns:92px minmax(0,1fr);gap:14px;align-items:center;padding:10px 2px;border-bottom:1px solid rgba(255,255,255,.055)}.status-guide-row:last-child{border-bottom:0}.status-guide-badge{display:flex;align-items:center;min-height:24px}.status-guide-row .tag{margin:0}.status-guide-copy{font-size:10px;line-height:1.55;color:var(--muted)}'
text = text[:start] + new_css + text[end:]

old_mobile = '.status-guide-grid{grid-template-columns:1fr}.status-guide-card{grid-template-columns:34px minmax(0,1fr);padding:10px}.status-guide-icon{width:34px;height:34px}\n'
if text.count(old_mobile) != 1:
    raise SystemExit(f'expected one old mobile status CSS block, found {text.count(old_mobile)}')
new_mobile = '.status-guide-row{grid-template-columns:84px minmax(0,1fr);gap:10px;padding:10px 2px}\n'
text = text.replace(old_mobile, new_mobile, 1)

block_start = '<div class="status-guide-grid" aria-label="Issue status guide">'
next_marker = '<div class="settings-rule-row"><strong>AI開発ルール</strong>'
start = text.find(block_start)
end = text.find(next_marker, start)
if start < 0 or end < 0:
    raise SystemExit('status guide HTML block not found')

rows = [
    ('START','review','対象作業を開始。'),
    ('NEXT','review','Phase統括が次の作業・進行先を決定。必要ならここで進捗率を更新。'),
    ('PASS','done','検証・レビュー成功。'),
    ('FAIL','blocked','検証・レビュー失敗。'),
    ('FIX','done','confirmed findingへの修正完了。'),
    ('BLOCKED','blocked','問題があり先へ進めない。'),
    ('WAITING','review','外部確認・入力など待機中。何待ちかは本文に書く。'),
    ('CLOSED','done','対象の完了条件を満たして終了。'),
    ('COST','cost','AI経理によるクレジット・時間・コスト記録。'),
]
new_block = '<div class="status-guide-list" aria-label="Issue status guide">' + ''.join(
    f'<div class="status-guide-row"><div class="status-guide-badge"><span class="tag {cls}">{label}</span></div><div class="status-guide-copy">{copy}</div></div>'
    for label, cls, copy in rows
) + '</div>'
text = text[:start] + new_block + text[end:]

checks = {
    'class="status-guide-list"': 1,
    'status-guide-icon': 0,
    'status-guide-card': 0,
    '<span class="tag review">START</span>': 1,
    '<span class="tag review">NEXT</span>': 1,
    '<span class="tag done">PASS</span>': 1,
    '<span class="tag blocked">FAIL</span>': 1,
    '<span class="tag done">FIX</span>': 1,
    '<span class="tag blocked">BLOCKED</span>': 1,
    '<span class="tag review">WAITING</span>': 1,
    '<span class="tag done">CLOSED</span>': 1,
    '<span class="tag cost">COST</span>': 1,
}
for marker, expected in checks.items():
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(f'marker count mismatch: {marker!r}: {actual} != {expected}')

path.write_text(text, encoding='utf-8')
