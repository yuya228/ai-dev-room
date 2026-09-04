from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old_css = '.status-guide-list{padding:8px 0 14px;border-bottom:1px solid var(--line)}.status-guide-row{display:grid;grid-template-columns:92px minmax(0,1fr);gap:14px;align-items:center;padding:10px 2px;border-bottom:1px solid rgba(255,255,255,.055)}.status-guide-row:last-child{border-bottom:0}.status-guide-badge{display:flex;align-items:center;min-height:24px}.status-guide-row .tag{margin:0}.status-guide-copy{font-size:10px;line-height:1.55;color:var(--muted)}'
new_css = '.status-guide-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:10px}.status-guide-item{min-width:0;padding:10px;border:1px solid var(--line);border-radius:9px;background:rgba(255,255,255,.02)}.status-guide-item .tag{display:inline-block;margin:0}.status-guide-copy{font-size:10px;line-height:1.5;color:var(--muted);margin-top:7px}'
if text.count(old_css) != 1:
    raise SystemExit(f'expected one old status CSS block, found {text.count(old_css)}')
text = text.replace(old_css, new_css, 1)

old_mobile = '.status-guide-row{grid-template-columns:84px minmax(0,1fr);gap:10px;padding:10px 2px}\n'
new_mobile = '.status-guide-grid{gap:7px}.status-guide-item{padding:8px}.status-guide-copy{font-size:9px;line-height:1.45}\n'
if text.count(old_mobile) != 1:
    raise SystemExit(f'expected one old mobile status CSS block, found {text.count(old_mobile)}')
text = text.replace(old_mobile, new_mobile, 1)

old_block_start = '<div class="status-guide-list" aria-label="Issue status guide">'
next_marker = '<div class="settings-rule-row"><strong>AI開発ルール</strong>'
start = text.find(old_block_start)
end = text.find(next_marker, start)
if start < 0 or end < 0:
    raise SystemExit('status guide HTML block not found')

items = [
    ('CLOSED','done','対象の完了条件を満たして終了。'),
    ('NEXT','review','Phase統括が次の作業・進行先を決定。必要ならここで進捗率を更新。'),
    ('WAITING','review','外部確認・入力など待機中。何待ちかは本文に書く。'),
    ('START','review','対象作業を開始。'),
    ('PASS','done','検証・レビュー成功。'),
    ('FAIL','blocked','検証・レビュー失敗。'),
    ('FIX','done','confirmed findingへの修正完了。'),
    ('BLOCKED','blocked','問題があり先へ進めない。'),
    ('COST','cost','AI経理によるクレジット・時間・コスト記録。'),
]
inner = ''.join(
    f'<div class="status-guide-item"><span class="tag {cls}">{label}</span><div class="status-guide-copy">{copy}</div></div>'
    for label, cls, copy in items
)
new_block = '<div class="settings-rule-row status-rule-row"><strong>STATUS</strong><div class="status-guide-grid" aria-label="Issue status guide">' + inner + '</div></div>'
text = text[:start] + new_block + text[end:]

checks = {
    'class="settings-rule-row status-rule-row"': 1,
    '<strong>STATUS</strong>': 1,
    'class="status-guide-grid"': 1,
    'status-guide-list': 0,
    'status-guide-row': 0,
}
for marker, expected in checks.items():
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(f'marker count mismatch: {marker!r}: {actual} != {expected}')

for label in ['CLOSED','NEXT','WAITING','START','PASS','FAIL','FIX','BLOCKED','COST']:
    if text.count(f'>{label}</span>') != 1:
        raise SystemExit(f'status marker mismatch: {label}')

path.write_text(text, encoding='utf-8')
