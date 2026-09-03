from pathlib import Path
import json

index_path = Path('index.html')
readme_path = Path('README.md')
manifest_path = Path('phase-manifest.json')
text = index_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one target, found {count}')
    text = text.replace(old, new, 1)


def replace_readme_once(old, new, label):
    global readme
    count = readme.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one target, found {count}')
    readme = readme.replace(old, new, 1)


replace_once(
    "const PROGRESS_API='https://api.github.com/repos/yuya228/ai-dev-room/issues/2/comments';",
    "const DEFAULT_PROGRESS_ISSUE_URL='https://github.com/yuya228/ai-dev-room/issues/2',DEFAULT_PROGRESS_API='https://api.github.com/repos/yuya228/ai-dev-room/issues/2/comments',PHASE_MANIFEST_URL='./phase-manifest.json';\nlet progressIssueUrl=DEFAULT_PROGRESS_ISSUE_URL,progressApi=DEFAULT_PROGRESS_API,activePhase=2,phaseManifestCache=null;",
    'phase source constants',
)

replace_once(
    "phase1:{name:'Phese1'",
    "phase1:{phase:1,name:'Phese1'",
    'phase1 metadata',
)

replace_once(
    "let current='progress',busy=false,",
    "let current='progress',busy=false,savedArchiveCaches={},",
    'state archive cache',
)

replace_once(
    "if(Array.isArray(saved?.progressCache))rooms.progress.messages=saved.progressCache.slice(-100);if(saved?.ui?.collapsedSections&&typeof saved.ui.collapsedSections==='object')",
    "if(Array.isArray(saved?.progressCache))rooms.progress.messages=saved.progressCache.slice(-100);if(saved?.phaseManifestCache&&typeof saved.phaseManifestCache==='object')phaseManifestCache=saved.phaseManifestCache;if(saved?.archiveCaches&&typeof saved.archiveCaches==='object')savedArchiveCaches=saved.archiveCaches;if(saved?.ui?.collapsedSections&&typeof saved.ui.collapsedSections==='object')",
    'restore phase manifest cache',
)

replace_once(
    "function customChannelItems(){return Object.entries(rooms).filter(([,r])=>r.type==='custom').map(([id,r])=>({id,name:r.name,desc:r.desc,sourceUrl:r.sourceUrl||'',cache:r.messages.slice(-100)}))}\nfunction saveState(){try{const channels={};for(const ch of ['chat','phase1','progress'])channels[ch]={name:rooms[ch].name,desc:rooms[ch].desc};localStorage.setItem(STORAGE_KEY,JSON.stringify({version:9,current,workspace:{name:workspaceMeta.name,sub:workspaceMeta.sub},rooms:{chat:{messages:rooms.chat.messages.slice(-200)}},channels,customChannels:customChannelItems(),unreadCounts,progressKnownId,progressCache:rooms.progress.messages.slice(-100),ui:{collapsedSections}}))}catch(e){console.warn('Chat save failed',e)}}",
    "function customChannelItems(){return Object.entries(rooms).filter(([,r])=>r.type==='custom').map(([id,r])=>({id,name:r.name,desc:r.desc,sourceUrl:r.sourceUrl||'',cache:r.messages.slice(-100)}))}\nfunction archiveCacheItems(){const out={};for(const [id,r] of Object.entries(rooms))if(r.type==='archive'&&r.sourceUrl)out[id]=r.messages.slice(-100);return out}\nfunction saveState(){try{const channels={};for(const ch of ['chat','phase1','progress'])if(rooms[ch])channels[ch]={name:rooms[ch].name,desc:rooms[ch].desc};localStorage.setItem(STORAGE_KEY,JSON.stringify({version:9,current,workspace:{name:workspaceMeta.name,sub:workspaceMeta.sub},rooms:{chat:{messages:rooms.chat.messages.slice(-200)}},channels,customChannels:customChannelItems(),unreadCounts,progressKnownId,progressCache:rooms.progress.messages.slice(-100),phaseManifestCache,archiveCaches:archiveCacheItems(),ui:{collapsedSections}}))}catch(e){console.warn('Chat save failed',e)}}",
    'save manifest and archive cache',
)

old_channel_order = "function channelOrder(){return ['chat','phase1','progress',...Object.keys(rooms).filter(ch=>rooms[ch].type==='custom')]}"
phase_functions = r'''function phaseArchiveId(phase){return `phase${Math.max(1,Math.floor(Number(phase)||1))}`}
function issueCommentsApi(info){return `https://api.github.com/repos/${encodeURIComponent(info.owner)}/${encodeURIComponent(info.repo)}/issues/${info.issue}/comments`}
function roomHasGitHubIssueSource(r){return !!r?.sourceUrl&&(r.type==='custom'||r.type==='archive')}
function normalizePhaseManifest(data){if(!data||Number(data.version)!==1)return null;const phase=Math.floor(Number(data.activePhase));if(!Number.isSafeInteger(phase)||phase<1)return null;const progressInfo=parseGitHubIssueUrl(data?.progress?.source?.url||'');if(!progressInfo||data?.progress?.source?.type!=='github_issue')return null;const archives=[],seen=new Set();for(const raw of Array.isArray(data.archives)?data.archives:[]){const p=Math.floor(Number(raw?.phase));if(!Number.isSafeInteger(p)||p<1||p===phase||seen.has(p))return null;seen.add(p);const sourceType=String(raw?.source?.type||'');let source={type:sourceType};if(sourceType==='github_issue'){const info=parseGitHubIssueUrl(raw?.source?.url||'');if(!info)return null;source={type:'github_issue',url:info.url,format:raw?.source?.format==='raw'?'raw':'progress'}}else if(sourceType!=='builtin')return null;archives.push({phase:p,name:String(raw?.name||`Phese${p}`).slice(0,24),desc:String(raw?.desc||`Phase ${p} 完了ログ`).slice(0,80),status:String(raw?.status||''),source})}archives.sort((a,b)=>a.phase-b.phase);return{version:1,activePhase:phase,progress:{source:{type:'github_issue',url:progressInfo.url}},archives}}
function resetProgressSourceState(){rooms.progress.messages=[];progressLoading=false;progressLoadingOlder=false;progressInitialized=false;progressNewestPage=1;progressOldestPage=1;progressHasOlder=false;progressOlderBuffer=[];progressSyncError='';lastProgressFetch=0;phaseProgress=0;progressKnownId='';delete unreadCounts.progress}
function applyPhaseManifest(data){const next=normalizePhaseManifest(data);if(!next)return false;const oldActive=activePhase,oldProgressUrl=progressIssueUrl,oldProgressMessages=rooms.progress.messages.slice(-100),keep=new Set();let archiveChanged=false;for(const spec of next.archives){const id=phaseArchiveId(spec.phase);keep.add(id);let r=rooms[id];if(spec.source.type==='builtin'){if(!r||r.type!=='archive')return false;const changed=r.phase!==spec.phase||r.name!==spec.name||r.desc!==spec.desc||!!r.sourceUrl;r.phase=spec.phase;r.name=spec.name;r.desc=spec.desc;r.type='archive';r.manifestManaged=true;r.placeholder=`Phase ${spec.phase} archive`;r.rule=`Phase ${spec.phase}の完了ログ · 読み取り専用アーカイブ。`;delete r.sourceUrl;delete r.sourceFormat;delete r.sourceState;archiveChanged=archiveChanged||changed;continue}const sourceUrl=spec.source.url,sourceFormat=spec.source.format;const existingSame=!!r&&r.type==='archive'&&r.sourceUrl===sourceUrl&&r.sourceFormat===sourceFormat;let cache=existingSame?r.messages:(Array.isArray(savedArchiveCaches[id])?savedArchiveCaches[id].slice(-100):[]);if(sourceUrl===oldProgressUrl&&sourceFormat==='progress'&&oldProgressMessages.length)cache=oldProgressMessages.slice(-100);if(!r||r.type!=='archive'){r=rooms[id]={phase:spec.phase,name:spec.name,desc:spec.desc,type:'archive',placeholder:`Phase ${spec.phase} archive`,rule:`Phase ${spec.phase}の完了ログ · GitHub Issueから読み取り専用で同期。`,messages:cache,sourceUrl,sourceFormat,manifestManaged:true};archiveChanged=true}else{const changed=!existingSame||r.phase!==spec.phase||r.name!==spec.name||r.desc!==spec.desc;r.phase=spec.phase;r.name=spec.name;r.desc=spec.desc;r.placeholder=`Phase ${spec.phase} archive`;r.rule=`Phase ${spec.phase}の完了ログ · GitHub Issueから読み取り専用で同期。`;r.manifestManaged=true;if(!existingSame){r.messages=cache;delete r.sourceState}r.sourceUrl=sourceUrl;r.sourceFormat=sourceFormat;archiveChanged=archiveChanged||changed}}
for(const [id,r] of Object.entries(rooms)){if(r.type==='archive'&&r.manifestManaged&&!keep.has(id)){if(current===id)current='progress';delete rooms[id];delete unreadCounts[id];archiveChanged=true}}
const progressInfo=parseGitHubIssueUrl(next.progress.source.url),nextApi=issueCommentsApi(progressInfo),progressChanged=progressIssueUrl!==progressInfo.url||progressApi!==nextApi;activePhase=next.activePhase;progressIssueUrl=progressInfo.url;progressApi=nextApi;rooms.progress.desc=`Phase ${activePhase}の活動ログ`;if(progressChanged)resetProgressSourceState();phaseManifestCache=next;if(oldActive!==activePhase||archiveChanged||progressChanged)renderChannelNav();return oldActive!==activePhase||archiveChanged||progressChanged}
async function loadPhaseManifest(){try{const res=await fetch(PHASE_MANIFEST_URL,{cache:'no-store'});if(!res.ok)throw new Error(`Phase manifest HTTP ${res.status}`);const data=await res.json();const normalized=normalizePhaseManifest(data);if(!normalized)throw new Error('Phase manifest invalid');const changed=applyPhaseManifest(normalized);phaseManifestCache=normalized;saveState();return changed}catch(e){const cached=normalizePhaseManifest(phaseManifestCache);if(cached){applyPhaseManifest(cached);console.warn('Phase manifest sync failed; keeping previous-good manifest',e);return false}console.warn('Phase manifest sync failed; using built-in Phase fallback',e);return false}}
function channelOrder(){const archives=Object.keys(rooms).filter(ch=>rooms[ch].type==='archive').sort((a,b)=>(rooms[a].phase||0)-(rooms[b].phase||0));return ['chat',...archives,'progress',...Object.keys(rooms).filter(ch=>rooms[ch].type==='custom')]}
'''
replace_once(old_channel_order, phase_functions.rstrip('\n'), 'phase manifest functions')

replace_once(
    "else if(r.type==='archive'){input.value='';input.placeholder='Phase 1 archive';sendBtn.textContent='読み取り専用';note.textContent='Phase 1 完了ログ · アーカイブ'}",
    "else if(r.type==='archive'){const p=r.phase||1,st=r.sourceUrl?customSourceState(r):null,info=r.sourceUrl?parseGitHubIssueUrl(r.sourceUrl):null;input.value='';input.placeholder=`Phase ${p} archive`;sendBtn.textContent='読み取り専用';note.textContent=r.sourceUrl?(st.loading?'Archiveを同期中…':st.syncError?'同期エラー · 前回正常データを表示中':info?`${info.owner}/${info.repo} #${info.issue} · Phase ${p} archive`:`Phase ${p} archive`):`Phase ${p} 完了ログ · アーカイブ`}",
    'archive composer status',
)
replace_once(
    "r.type==='archive'?'Phase 1 archive'",
    "r.type==='archive'?`Phase ${r.phase||1} archive`",
    'archive readonly label',
)
replace_once(
    "else if(r.type==='archive'){empty='Phase 1ログはまだ登録されていません。';dayLabel='PHASE 1 ARCHIVE'}",
    "else if(r.type==='archive'){const p=r.phase||1,st=r.sourceUrl?customSourceState(r):null;empty=r.sourceUrl?(st.loading?'Archiveを同期中…':st.syncError?'Archiveの同期に失敗しました。':'Archiveログはまだ空です。'):`Phase ${p}ログはまだ登録されていません。`;dayLabel=`PHASE ${p} ARCHIVE`}",
    'archive render state',
)
replace_once(
    "showAudit=r.type==='progress'&&meta.recordedBy&&meta.recordedBy!==meta.actor",
    "showAudit=(r.type==='progress'||r.sourceFormat==='progress')&&meta.recordedBy&&meta.recordedBy!==meta.actor",
    'archive canonical audit',
)

replace_once(
    "function parseGitHubIssueComment(c){const login=String(c?.user?.login||'GitHub'),body=String(c?.body||'').trim()||'(内容なし)',time=new Date(c?.created_at||Date.now()).toLocaleString('ja-JP',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});return['system',body,time,[],{commentId:String(c?.id||''),displayName:`@${login}`,role:'GitHub',avatar:'GH'}]}\nfunction customMessageId",
    "function parseGitHubIssueComment(c){const login=String(c?.user?.login||'GitHub'),body=String(c?.body||'').trim()||'(内容なし)',time=new Date(c?.created_at||Date.now()).toLocaleString('ja-JP',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});return['system',body,time,[],{commentId:String(c?.id||''),displayName:`@${login}`,role:'GitHub',avatar:'GH'}]}\nfunction parseIssueMessageForRoom(r,c){return r?.sourceFormat==='progress'?parseCanonical(c):parseGitHubIssueComment(c)}\nfunction customMessageId",
    'archive source parser',
)
replace_once(
    "const parsed=(Array.isArray(data)?data:[]).map(parseGitHubIssueComment)",
    "const parsed=(Array.isArray(data)?data:[]).map(c=>parseIssueMessageForRoom(r,c))",
    'generic source merge parser',
)
replace_once(
    "if(current!==ch||r?.type!=='custom'||!r.sourceUrl)return",
    "if(current!==ch||!roomHasGitHubIssueSource(r))return",
    'generic older source guard',
)
replace_once(
    "if(r?.type!=='custom'||!r.sourceUrl)return",
    "if(!roomHasGitHubIssueSource(r))return",
    'generic source guard',
)
replace_once(
    "r.messages=latestData.map(parseGitHubIssueComment)",
    "r.messages=latestData.map(c=>parseIssueMessageForRoom(r,c))",
    'generic initial parser',
)

replace_once(
    "function progressUrl(page){return `${PROGRESS_API}?per_page=100&page=${Math.max(1,Math.floor(Number(page)||1))}`}",
    "function progressUrl(page){return `${progressApi}?per_page=100&page=${Math.max(1,Math.floor(Number(page)||1))}`}",
    'dynamic progress API',
)

replace_once(
    "async function setChannel(ch){if(!rooms[ch])return;closeSettings();resetSearch();current=ch;saveState();closeDrawer();render();if(ch==='progress')await loadCanonicalProgress(true);else if(rooms[ch]?.type==='custom'&&rooms[ch]?.sourceUrl)await loadCustomIssueChannel(ch,false)}",
    "async function setChannel(ch){if(!rooms[ch])return;closeSettings();resetSearch();current=ch;saveState();closeDrawer();render();if(ch==='progress')await loadCanonicalProgress(true);else if(roomHasGitHubIssueSource(rooms[ch]))await loadCustomIssueChannel(ch,false);scrollFeedToLatest()}",
    'open channel at latest',
)

replace_once(
    "closeChannelEditor();render();if(r.type==='custom'&&r.sourceUrl)loadCustomIssueChannel(ch,true)}",
    "closeChannelEditor();render();if(r.type==='custom'&&r.sourceUrl)loadCustomIssueChannel(ch,true).then(()=>{if(current===ch)scrollFeedToLatest()})}",
    'new custom channel latest',
)

replace_once(
    "function syncFeedScrollState(){syncJumpBottom();if(isFeedAtBottom())markRead(current);if(feed.scrollTop<=80){if(current==='progress')loadOlderProgress();else if(rooms[current]?.type==='custom'&&rooms[current]?.sourceUrl)loadOlderCustomIssue(current)}}\nfunction jumpToBottom(){feed.scrollTo({top:feed.scrollHeight,behavior:'smooth'})}",
    "function syncFeedScrollState(){syncJumpBottom();if(isFeedAtBottom())markRead(current);if(feed.scrollTop<=80){if(current==='progress')loadOlderProgress();else if(roomHasGitHubIssueSource(rooms[current]))loadOlderCustomIssue(current)}}\nfunction jumpToBottom(){feed.scrollTo({top:feed.scrollHeight,behavior:'smooth'})}\nfunction scrollFeedToLatest(){requestAnimationFrame(()=>{feed.scrollTop=feed.scrollHeight;syncJumpBottom();markRead(current)})}",
    'generic older scroll and latest helper',
)

replace_once(
    "document.getElementById('settingsSync').addEventListener('click',()=>loadCanonicalProgress(true));",
    "document.getElementById('settingsSync').addEventListener('click',async()=>{await loadPhaseManifest();await loadCanonicalProgress(true);if(roomHasGitHubIssueSource(rooms[current]))await loadCustomIssueChannel(current,true)});",
    'settings manifest resync',
)

replace_once(
    "setInterval(()=>{loadCanonicalProgress(true);if(rooms[current]?.type==='custom'&&rooms[current]?.sourceUrl)loadCustomIssueChannel(current,true)},300000);syncAppHeight(true);render();loadCanonicalProgress(false);",
    "setInterval(async()=>{await loadPhaseManifest();await loadCanonicalProgress(true);if(roomHasGitHubIssueSource(rooms[current]))await loadCustomIssueChannel(current,true)},300000);async function boot(){syncAppHeight(true);await loadPhaseManifest();render();if(current==='progress')await loadCanonicalProgress(false);else if(roomHasGitHubIssueSource(rooms[current]))await loadCustomIssueChannel(current,false);scrollFeedToLatest()}boot();",
    'manifest-aware boot and polling',
)

replace_readme_once(
    "- **GitHub Issue #2** — `#Progress` の記録元\n",
    "- **`phase-manifest.json`** — 現在Phase・Progress source・完了Phase archiveの構成元\n- **GitHub Issue** — `#Progress` / 動的Archiveの読み取り元\n",
    'readme architecture',
)
replace_readme_once(
    "現在進行中のPhase専用ログ。現在はPhase 2を記録する。",
    "現在進行中のPhase専用ログ。対象PhaseとGitHub Issueは `phase-manifest.json` から決まり、現在はPhase 2を記録する。",
    'readme progress source',
)
replace_readme_once(
    "Phase完了後は重要ログを `#PheseN` に固定し、`#Progress` は次のPhaseへ切り替える。",
    "Phase完了後は、ユーザーが明示的に次Phase開始を承認した後だけPhase統括が `phase-manifest.json` を更新する。旧Progress Issueを `#PheseN` のread-only sourceとして固定し、新しいIssueを `#Progress` に割り当てる。進捗率100%だけでは切り替えない。",
    'readme transition rule',
)

anchor = "### `#PheseN`\n\n完了済みPhaseの読み取り専用アーカイブ。\n\n- 当時の重要イベントを会話形式で残す\n- 完了後は原則変更しない\n- 厳密な証拠は元のGitHub / handoff / reviewを参照する\n"
addition = anchor + "\n### Phase切替の担当\n\nPhase切替はブラウザから実行しない。AI Dev RoomはmanifestとGitHub Issueを読むだけにする。\n\n1. ユーザーが現在Phaseの完了と次Phase開始を明示承認する\n2. Phase統括が旧Progress Issueを完了Archiveとして確定し、必要ならclose / lockする\n3. Phase統括が次Phase用のcanonical Progress Issueを作成または指定する\n4. Phase統括が `phase-manifest.json` の `activePhase` / `progress` / `archives` を更新する\n5. AI Dev Roomはmanifestを再読込し、旧Phaseを `#PheseN`、新Phaseを `#Progress` として自動表示する\n\nCodexはこの仕組み自体の実装・修正担当、Work QAは仕組み変更時の独立レビュー担当とする。通常のPhase切替判断は行わない。\n"
replace_readme_once(anchor, addition, 'readme phase switch owner')

manifest = {
    "version": 1,
    "activePhase": 2,
    "progress": {
        "source": {
            "type": "github_issue",
            "url": "https://github.com/yuya228/ai-dev-room/issues/2",
        }
    },
    "archives": [
        {
            "phase": 1,
            "name": "Phese1",
            "desc": "Phase 1 完了ログ",
            "status": "PASS",
            "source": {"type": "builtin"},
        }
    ],
    "transitionPolicy": {
        "requiresExplicitUserApproval": True,
        "executor": "Phase統括",
        "browserWriteAccess": False,
    },
}

index_path.write_text(text, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
