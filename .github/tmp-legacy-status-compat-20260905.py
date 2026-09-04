from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
old = """const ISSUE_STATUSES=['START','NEXT','PASS','FAIL','FIX','BLOCKED','WAITING','CLOSED','COST'];
function normalizeIssueStatus(status){const s=String(status||'').trim().toUpperCase();return ISSUE_STATUSES.includes(s)?s:'LOG'}
function tagClass(status){const s=normalizeIssueStatus(status);if(['PASS','CLOSED','FIX'].includes(s))return'done';if(s==='COST')return'cost';if(['BLOCKED','FAIL'].includes(s))return'blocked';if(s==='LOG')return'log';return'review'}
function issueDisplayTags(tags){const list=Array.isArray(tags)?tags:[];if(!list.length)return[];for(const t of list){const s=String(t?.[0]||'').trim().toUpperCase();if(ISSUE_STATUSES.includes(s))return[[s,tagClass(s)]]}return[['LOG','log']]}
"""
new = """const ISSUE_STATUSES=['START','NEXT','PASS','FAIL','FIX','BLOCKED','WAITING','CLOSED','COST'],LEGACY_STATUS_CUTOFF='2026-09-05 01:38 JST';
function normalizeIssueStatus(status){const s=String(status||'').trim().toUpperCase();return ISSUE_STATUSES.includes(s)?s:'LOG'}
function legacyStatusFromTags(tags){const list=Array.isArray(tags)?tags:[];if(!list.length)return'LOG';for(const t of list){const s=String(t?.[0]||'').trim().toUpperCase();if(ISSUE_STATUSES.includes(s))return s}const priority=['CLOSED','BLOCKED','FAIL','FIX','WAITING','PASS','START','NEXT','COST'];for(const wanted of priority){for(const t of list){const words=String(t?.[0]||'').trim().toUpperCase().split(/[^A-Z0-9]+/).filter(Boolean);if(words.includes(wanted))return wanted}}return'LOG'}
function isLegacyCanonicalTime(value){const t=String(value||'').trim();return /^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2} JST$/.test(t)&&t<=LEGACY_STATUS_CUTOFF}
function normalizeCanonicalStatus(status,actor,time){const s=String(status||'').trim().toUpperCase();if(ISSUE_STATUSES.includes(s))return s;if(!isLegacyCanonicalTime(time))return'LOG';if(actor==='AI経理'&&s==='LOG')return'COST';if(s==='DONE')return'PASS';if(s==='IN_PROGRESS')return'START';const words=s.split(/[^A-Z0-9]+/).filter(Boolean);for(const wanted of ['CLOSED','BLOCKED','FAIL','FIX','WAITING','PASS','START','NEXT','COST'])if(words.includes(wanted))return wanted;return'LOG'}
function tagClass(status){const s=normalizeIssueStatus(status);if(['PASS','CLOSED','FIX'].includes(s))return'done';if(s==='COST')return'cost';if(['BLOCKED','FAIL'].includes(s))return'blocked';if(s==='LOG')return'log';return'review'}
function issueDisplayTags(tags){const status=legacyStatusFromTags(tags);return[[status,tagClass(status)]]}
"""
if text.count(old) != 1:
    raise SystemExit(f'status block target count={text.count(old)}')
text = text.replace(old, new, 1)
old2 = "status=normalizeIssueStatus(header?.[3]||'LOG'),time=header?.[1]||"
new2 = "status=normalizeCanonicalStatus(header?.[3]||'LOG',actor,header?.[1]),time=header?.[1]||"
if text.count(old2) != 1:
    raise SystemExit(f'parseCanonical target count={text.count(old2)}')
text = text.replace(old2, new2, 1)
path.write_text(text, encoding='utf-8')
