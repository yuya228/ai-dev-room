from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old_guard = "if(!Number.isSafeInteger(p)||p<1||p===phase||seen.has(p))return null;"
new_guard = "if(!Number.isSafeInteger(p)||p<1||p>=phase||seen.has(p))return null;"
if text.count(old_guard) != 1:
    raise SystemExit(f'archive phase guard target count={text.count(old_guard)}')
text = text.replace(old_guard, new_guard, 1)

old_tail = "archives.sort((a,b)=>a.phase-b.phase);return{version:1,activePhase:phase,progress:{source:{type:'github_issue',url:progressInfo.url}},archives}}"
new_tail = "archives.sort((a,b)=>a.phase-b.phase);if(archives.length!==Math.max(0,phase-1)||archives.some((a,i)=>a.phase!==i+1))return null;if(archives.some(a=>a.source.type==='github_issue'&&a.source.url===progressInfo.url))return null;const policy=data?.transitionPolicy;if(policy?.requiresExplicitUserApproval!==true||policy?.executor!=='Phase統括'||policy?.browserWriteAccess!==false)return null;return{version:1,activePhase:phase,progress:{source:{type:'github_issue',url:progressInfo.url}},archives,transitionPolicy:{requiresExplicitUserApproval:true,executor:'Phase統括',browserWriteAccess:false}}}"
if text.count(old_tail) != 1:
    raise SystemExit(f'normalization tail target count={text.count(old_tail)}')
text = text.replace(old_tail, new_tail, 1)

path.write_text(text, encoding='utf-8')
