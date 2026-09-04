from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

# 1) Neutral LOG visual fallback.
old_css = ".cost{color:#a9d9ff;border-color:rgba(98,182,255,.25);background:rgba(98,182,255,.06)}"
new_css = old_css + ".log{color:#bcb5c4;border-color:rgba(255,255,255,.12);background:rgba(255,255,255,.025)}"
if text.count(old_css) != 1:
    raise SystemExit(f'cost css marker count: {text.count(old_css)}')
text = text.replace(old_css, new_css, 1)

# 2) Document fallback behavior without adding LOG to the official 3x3 statuses.
old_status_head = '<div class="settings-rule-row status-rule-row"><strong>STATUS</strong><div class="status-guide-grid" aria-label="Issue status guide">'
new_status_head = '<div class="settings-rule-row status-rule-row"><strong>STATUS</strong><span>正式STATUSは下記9種。その他はLOGとして表示。</span><div class="status-guide-grid" aria-label="Issue status guide">'
if text.count(old_status_head) != 1:
    raise SystemExit(f'status head marker count: {text.count(old_status_head)}')
text = text.replace(old_status_head, new_status_head, 1)

# 3) Canonical status set + normalization + one-tag archive display.
old_fn = "function tagClass(status){const s=String(status||'').toUpperCase();if(['DONE','PASS','CLOSED','READY'].includes(s))return'done';if(['COST','CREDIT'].includes(s))return'cost';if(['BLOCKED','HIGH','FAIL'].includes(s))return'blocked';return'review'}"
new_fn = "const ISSUE_STATUSES=['START','NEXT','PASS','FAIL','FIX','BLOCKED','WAITING','CLOSED','COST'];\nfunction normalizeIssueStatus(status){const s=String(status||'').trim().toUpperCase();return ISSUE_STATUSES.includes(s)?s:'LOG'}\nfunction tagClass(status){const s=normalizeIssueStatus(status);if(['PASS','CLOSED','FIX'].includes(s))return'done';if(s==='COST')return'cost';if(['BLOCKED','FAIL'].includes(s))return'blocked';if(s==='LOG')return'log';return'review'}\nfunction issueDisplayTags(tags){const list=Array.isArray(tags)?tags:[];if(!list.length)return[];for(const t of list){const s=String(t?.[0]||'').trim().toUpperCase();if(ISSUE_STATUSES.includes(s))return[[s,tagClass(s)]]}return[['LOG','log']]}"
if text.count(old_fn) != 1:
    raise SystemExit(f'tagClass marker count: {text.count(old_fn)}')
text = text.replace(old_fn, new_fn, 1)

# 4) GitHub canonical comments: unknown status becomes LOG immediately.
old_parse_part = "const actor=header?.[2]||'Phase統括',status=header?.[3]||'LOG',time=header?.[1]||"
new_parse_part = "const actor=header?.[2]||'Phase統括',status=normalizeIssueStatus(header?.[3]||'LOG'),time=header?.[1]||"
if text.count(old_parse_part) != 1:
    raise SystemExit(f'parse status marker count: {text.count(old_parse_part)}')
text = text.replace(old_parse_part, new_parse_part, 1)

# 5) Search the status the user actually sees for archive/progress rooms.
old_search = "function messageMatchesSearch(m,q){const a=agents[m[0]]||agents.system,meta=m[4]||{},tags=(m[3]||[]).map(t=>t?.[0]||'');return[meta.displayName||a.name,meta.role||a.role,m[1],m[2],...tags].join('\\n').toLocaleLowerCase('ja-JP').includes(q)}"
new_search = "function messageMatchesSearch(m,q,r=rooms[current]){const a=agents[m[0]]||agents.system,meta=m[4]||{},sourceTags=(r?.type==='archive'||r?.type==='progress'||r?.sourceFormat==='progress')?issueDisplayTags(m[3]):(m[3]||[]),tags=sourceTags.map(t=>t?.[0]||'');return[meta.displayName||a.name,meta.role||a.role,m[1],m[2],...tags].join('\\n').toLocaleLowerCase('ja-JP').includes(q)}"
if text.count(old_search) != 1:
    raise SystemExit(f'search marker count: {text.count(old_search)}')
text = text.replace(old_search, new_search, 1)
text = text.replace("r.messages.filter(m=>messageMatchesSearch(m,q))", "r.messages.filter(m=>messageMatchesSearch(m,q,r))", 1)

# 6) Archive/progress messages render exactly one official status, or one LOG fallback.
old_map_start = "feed.innerHTML='<div class=\"day\">'+dayLabel+'</div>'+list.map(m=>{const a=agents[m[0]]||agents.system,meta=m[4]||{},showAudit="
new_map_start = "feed.innerHTML='<div class=\"day\">'+dayLabel+'</div>'+list.map(m=>{const a=agents[m[0]]||agents.system,meta=m[4]||{},displayTags=(r.type==='archive'||r.type==='progress'||r.sourceFormat==='progress')?issueDisplayTags(m[3]):(m[3]||[]),showAudit="
if text.count(old_map_start) != 1:
    raise SystemExit(f'render map marker count: {text.count(old_map_start)}')
text = text.replace(old_map_start, new_map_start, 1)
old_render_tags = "${m[3]?.length?`<div class=\"tags\">${m[3].map(t=>`<span class=\"tag ${t[1]}\">${esc(t[0])}</span>`).join('')}</div>`:''}"
new_render_tags = "${displayTags.length?`<div class=\"tags\">${displayTags.map(t=>`<span class=\"tag ${t[1]}\">${esc(t[0])}</span>`).join('')}</div>`:''}"
if text.count(old_render_tags) != 1:
    raise SystemExit(f'render tags marker count: {text.count(old_render_tags)}')
text = text.replace(old_render_tags, new_render_tags, 1)

# Static checks.
checks = {
    "const ISSUE_STATUSES=['START','NEXT','PASS','FAIL','FIX','BLOCKED','WAITING','CLOSED','COST'];": 1,
    "function normalizeIssueStatus(status)": 1,
    "function issueDisplayTags(tags)": 1,
    "その他はLOGとして表示。": 1,
    ".log{color:#bcb5c4": 1,
    "displayTags=(r.type==='archive'||r.type==='progress'||r.sourceFormat==='progress')?issueDisplayTags(m[3]):(m[3]||[])": 1,
}
for marker, expected in checks.items():
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(f'marker count mismatch {marker!r}: {actual} != {expected}')

path.write_text(text, encoding='utf-8')
