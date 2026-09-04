from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

css_old = ".settings-rule-row{padding:14px 2px;border-bottom:1px solid var(--line)}.settings-rule-row:first-child{border-top:1px solid var(--line)}.settings-rule-row strong{display:block;font-size:13px}.settings-rule-row span{display:block;font-size:11px;line-height:1.65;color:var(--muted);margin-top:4px}"
css_new = css_old + ".status-guide-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:14px 0;border-bottom:1px solid var(--line)}.status-guide-card{min-width:0;display:grid;grid-template-columns:36px minmax(0,1fr);gap:10px;align-items:center;padding:11px;border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.02)}.status-guide-icon{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.035);color:#cfc9d5}.status-guide-icon svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}.status-guide-copy{min-width:0}.status-guide-copy strong{display:block;font-size:12px;line-height:1.2}.status-guide-copy span{display:block;font-size:10px;line-height:1.5;color:var(--muted);margin-top:4px}.status-guide-card.start .status-guide-icon,.status-guide-card.next .status-guide-icon{color:#b7abff;background:rgba(124,92,255,.08);border-color:rgba(124,92,255,.22)}.status-guide-card.pass .status-guide-icon,.status-guide-card.closed .status-guide-icon{color:#aef0cf;background:rgba(66,211,146,.07);border-color:rgba(66,211,146,.2)}.status-guide-card.fail .status-guide-icon,.status-guide-card.blocked .status-guide-icon{color:#ffb4c1;background:rgba(255,95,126,.07);border-color:rgba(255,95,126,.2)}.status-guide-card.fix .status-guide-icon,.status-guide-card.waiting .status-guide-icon{color:#ffe1a3;background:rgba(255,204,102,.07);border-color:rgba(255,204,102,.2)}.status-guide-card.cost .status-guide-icon{color:#a9d9ff;background:rgba(98,182,255,.07);border-color:rgba(98,182,255,.2)}"
if text.count(css_old) != 1:
    raise SystemExit(f'expected one CSS target, found {text.count(css_old)}')
text = text.replace(css_old, css_new, 1)

mobile_old = "@media(max-width:720px){\nhtml,body{height:100dvh;min-height:100dvh}"
mobile_new = "@media(max-width:720px){\n.status-guide-grid{grid-template-columns:1fr}.status-guide-card{grid-template-columns:34px minmax(0,1fr);padding:10px}.status-guide-icon{width:34px;height:34px}\nhtml,body{height:100dvh;min-height:100dvh}"
if text.count(mobile_old) != 1:
    raise SystemExit(f'expected one mobile target, found {text.count(mobile_old)}')
text = text.replace(mobile_old, mobile_new, 1)

status_old = '<div class="settings-rule-row"><strong>START</strong><span>対象作業を開始。</span></div><div class="settings-rule-row"><strong>NEXT</strong><span>Phase統括が次の作業・進行先を決定。必要ならここで進捗率を更新。</span></div><div class="settings-rule-row"><strong>PASS</strong><span>検証・レビュー成功。</span></div><div class="settings-rule-row"><strong>FAIL</strong><span>検証・レビュー失敗。</span></div><div class="settings-rule-row"><strong>FIX</strong><span>confirmed findingへの修正完了。</span></div><div class="settings-rule-row"><strong>BLOCKED</strong><span>問題があり先へ進めない。</span></div><div class="settings-rule-row"><strong>WAITING</strong><span>外部確認・入力など待機中。何待ちかは本文に書く。</span></div><div class="settings-rule-row"><strong>CLOSED</strong><span>対象の完了条件を満たして終了。</span></div><div class="settings-rule-row"><strong>COST</strong><span>AI経理によるクレジット・時間・コスト記録。</span></div>'

status_new = '''<div class="status-guide-grid" aria-label="Issue status guide">
<div class="status-guide-card start"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5l11 7-11 7z"></path></svg></div><div class="status-guide-copy"><strong>START</strong><span>対象作業を開始。</span></div></div>
<div class="status-guide-card next"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14"></path><path d="M14 7l5 5-5 5"></path></svg></div><div class="status-guide-copy"><strong>NEXT</strong><span>Phase統括が次の作業・進行先を決定。必要ならここで進捗率を更新。</span></div></div>
<div class="status-guide-card pass"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12l4 4L19 6"></path></svg></div><div class="status-guide-copy"><strong>PASS</strong><span>検証・レビュー成功。</span></div></div>
<div class="status-guide-card fail"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M6 6l12 12"></path><path d="M18 6L6 18"></path></svg></div><div class="status-guide-copy"><strong>FAIL</strong><span>検証・レビュー失敗。</span></div></div>
<div class="status-guide-card fix"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M14.7 6.3a4 4 0 0 0-5-5l2.2 2.2-2.4 2.4-2.2-2.2a4 4 0 0 0 5 5l-7.6 7.6a2.1 2.1 0 0 0 3 3l7.6-7.6a4 4 0 0 0 5-5l-2.2 2.2-2.4-2.4 2.2-2.2a4 4 0 0 0-5 0z"></path></svg></div><div class="status-guide-copy"><strong>FIX</strong><span>confirmed findingへの修正完了。</span></div></div>
<div class="status-guide-card blocked"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7.5 2h9L22 7.5v9L16.5 22h-9L2 16.5v-9z"></path><path d="M8 8l8 8"></path></svg></div><div class="status-guide-copy"><strong>BLOCKED</strong><span>問題があり先へ進めない。</span></div></div>
<div class="status-guide-card waiting"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path></svg></div><div class="status-guide-copy"><strong>WAITING</strong><span>外部確認・入力など待機中。何待ちかは本文に書く。</span></div></div>
<div class="status-guide-card closed"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"></circle><path d="M8 12l3 3 5-6"></path></svg></div><div class="status-guide-copy"><strong>CLOSED</strong><span>対象の完了条件を満たして終了。</span></div></div>
<div class="status-guide-card cost"><div class="status-guide-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 4l5 7 5-7"></path><path d="M8 11h8"></path><path d="M8 15h8"></path><path d="M12 11v8"></path></svg></div><div class="status-guide-copy"><strong>COST</strong><span>AI経理によるクレジット・時間・コスト記録。</span></div></div>
</div>'''.replace('\n','')

if text.count(status_old) != 1:
    raise SystemExit(f'expected one status block, found {text.count(status_old)}')
text = text.replace(status_old, status_new, 1)

for marker in ['class="status-guide-grid"','status-guide-card start','status-guide-card next','status-guide-card pass','status-guide-card fail','status-guide-card fix','status-guide-card blocked','status-guide-card waiting','status-guide-card closed','status-guide-card cost']:
    if text.count(marker) != 1:
        raise SystemExit(f'marker count mismatch: {marker} -> {text.count(marker)}')

path.write_text(text, encoding='utf-8')
