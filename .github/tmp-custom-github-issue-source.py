from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one target, found {count}')
    text = text.replace(old, new, 1)


replace_once(
    ".channel-editor-field input:focus{border-color:rgba(124,92,255,.65)}.channel-editor-actions",
    ".channel-editor-field input:focus{border-color:rgba(124,92,255,.65)}.channel-editor-help{font-size:10px;line-height:1.5;color:var(--muted);margin-top:6px}.channel-editor-error{min-height:15px;font-size:10px;line-height:1.5;color:#ff9aae;margin-top:4px}.channel-editor-actions",
    'editor source styles',
)

replace_once(
    '<div class="channel-editor-actions"><button id="channelEditCancel">キャンセル</button><button class="primary" id="channelEditSave">保存</button></div>',
    '<div class="channel-editor-field" id="channelSourceField" hidden><label for="channelSourceInput">GitHub Issue URL</label><input id="channelSourceInput" maxlength="240" autocomplete="off" inputmode="url" placeholder="https://github.com/owner/repo/issues/123"><div class="channel-editor-help">公開GitHub Issueのみ · コメントを読み取り専用で同期</div><div class="channel-editor-error" id="channelSourceError" aria-live="polite"></div></div><div class="channel-editor-actions"><button id="channelEditCancel">キャンセル</button><button class="primary" id="channelEditSave">保存</button></div>',
    'editor source field',
)

replace_once(
    "if(Array.isArray(saved?.customChannels)){for(const item of saved.customChannels.slice(0,20)){const id=String(item?.id||'');if(!/^custom-[a-z0-9-]+$/i.test(id)||rooms[id])continue;rooms[id]={name:String(item?.name||'Channel').slice(0,24),desc:String(item?.desc||'').slice(0,80),type:'custom',placeholder:'読み取り専用',rule:'このチャンネルは読み取り専用です。',messages:[]}}}",
    "if(Array.isArray(saved?.customChannels)){for(const item of saved.customChannels.slice(0,20)){const id=String(item?.id||'');if(!/^custom-[a-z0-9-]+$/i.test(id)||rooms[id])continue;const sourceUrl=String(item?.sourceUrl||'').slice(0,240);rooms[id]={name:String(item?.name||'Channel').slice(0,24),desc:String(item?.desc||'').slice(0,80),type:'custom',placeholder:'読み取り専用',rule:sourceUrl?'GitHub Issueのコメントを読み取り専用で同期します。':'このチャンネルは読み取り専用です。',messages:Array.isArray(item?.cache)?item.cache.slice(-100):[],sourceUrl}}}",
    'custom restore',
)

replace_once(
    "channelNameInput=document.getElementById('channelNameInput'),channelDescInput=document.getElementById('channelDescInput');",
    "channelNameInput=document.getElementById('channelNameInput'),channelDescInput=document.getElementById('channelDescInput'),channelSourceField=document.getElementById('channelSourceField'),channelSourceInput=document.getElementById('channelSourceInput'),channelSourceError=document.getElementById('channelSourceError');",
    'editor source elements',
)

replace_once(
    "return !!el&&(el===input||el===channelNameInput||el===channelDescInput||el===searchInput)",
    "return !!el&&(el===input||el===channelNameInput||el===channelDescInput||el===channelSourceInput||el===searchInput)",
    'editing field detection',
)

replace_once(
    "function customChannelItems(){return Object.entries(rooms).filter(([,r])=>r.type==='custom').map(([id,r])=>({id,name:r.name,desc:r.desc}))}",
    "function customChannelItems(){return Object.entries(rooms).filter(([,r])=>r.type==='custom').map(([id,r])=>({id,name:r.name,desc:r.desc,sourceUrl:r.sourceUrl||'',cache:r.messages.slice(-100)}))}",
    'custom persistence',
)

replace_once(
    "function messageMatchesSearch(m,q){const a=agents[m[0]]||agents.system,tags=(m[3]||[]).map(t=>t?.[0]||'');return[a.name,a.role,m[1],m[2],...tags].join('",
    "function messageMatchesSearch(m,q){const a=agents[m[0]]||agents.system,meta=m[4]||{},tags=(m[3]||[]).map(t=>t?.[0]||'');return[meta.displayName||a.name,meta.role||a.role,m[1],m[2],...tags].join('",
    'search custom author metadata',
)

replace_once(
    "return `<article class=\"msg\"><div class=\"avatar ${a.cls}\">${a.avatar}</div><div><div class=\"meta\"><span class=\"name\">${a.name}</span><span class=\"role\">${a.role}</span><span class=\"time\">${esc(m[2]||'')}</span>${showAudit?`<span class=\"audit\">recorded by ${esc(meta.recordedBy)}</span>`:''}</div>",
    "const displayName=meta.displayName||a.name,displayRole=meta.role||a.role,displayAvatar=meta.avatar||a.avatar;return `<article class=\"msg\"><div class=\"avatar ${a.cls}\">${esc(displayAvatar)}</div><div><div class=\"meta\"><span class=\"name\">${esc(displayName)}</span><span class=\"role\">${esc(displayRole)}</span><span class=\"time\">${esc(m[2]||'')}</span>${showAudit?`<span class=\"audit\">recorded by ${esc(meta.recordedBy)}</span>`:''}</div>",
    'custom author rendering',
)

replace_once(
    "else if(r.type==='custom'){empty='まだログはありません。';dayLabel='READ ONLY'}",
    "else if(r.type==='custom'){const st=customSourceState(r);empty=r.sourceUrl?(st.loading?'GitHub Issueを同期中…':st.syncError?'GitHub Issueの同期に失敗しました。':'コメントはまだありません。'):'GitHub Issue URLを設定してください。';dayLabel=r.sourceUrl?'GITHUB ISSUE':'READ ONLY'}",
    'custom empty state',
)

replace_once(
    "else if(r.type==='custom'){input.value='';input.placeholder=`#${normalizedRoomName(current)} · 読み取り専用`;sendBtn.textContent='読み取り専用';note.textContent='このチャンネルは読み取り専用'}",
    "else if(r.type==='custom'){const st=customSourceState(r),info=parseGitHubIssueUrl(r.sourceUrl||'');input.value='';input.placeholder=r.sourceUrl?'GitHub Issueから同期されます':`#${normalizedRoomName(current)} · 読み取り専用`;sendBtn.textContent='読み取り専用';note.textContent=st.loading?'GitHub Issueを同期中…':st.syncError?'同期エラー · 前回正常データを表示中':info?`${info.owner}/${info.repo} #${info.issue} · 読み取り専用`:'GitHub Issue URLを設定してください'}",
    'custom composer status',
)

replace_once(
    "function syncFeedScrollState(){syncJumpBottom();if(isFeedAtBottom())markRead(current);if(current==='progress'&&feed.scrollTop<=80)loadOlderProgress()}",
    "function syncFeedScrollState(){syncJumpBottom();if(isFeedAtBottom())markRead(current);if(feed.scrollTop<=80){if(current==='progress')loadOlderProgress();else if(rooms[current]?.type==='custom'&&rooms[current]?.sourceUrl)loadOlderCustomIssue(current)}}",
    'custom older-scroll hook',
)

insert_before = "function historyForApi(){return rooms.chat.messages.slice(-12).filter(m=>m[0]!=='system').map(m=>({speaker:agents[m[0]]?.name||m[0],text:m[1]}))}"
custom_source_js = r"""function parseGitHubIssueUrl(value){try{const u=new URL(String(value||'').trim());if(u.protocol!=='https:'||u.hostname!=='github.com'||u.search||u.hash)return null;const m=u.pathname.match(/^\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)\/issues\/(\d+)\/?$/);if(!m)return null;const issue=Number(m[3]);if(!Number.isSafeInteger(issue)||issue<1)return null;return{owner:m[1],repo:m[2],issue,url:`https://github.com/${m[1]}/${m[2]}/issues/${issue}`}}catch{return null}}
function customSourceState(r){if(!r.sourceState)r.sourceState={loading:false,loadingOlder:false,initialized:false,newestPage:1,oldestPage:1,hasOlder:false,olderBuffer:[],syncError:'',lastFetch:0};return r.sourceState}
function resetCustomSourceState(r){delete r.sourceState;return customSourceState(r)}
function customIssuePageUrl(r,page){const info=parseGitHubIssueUrl(r?.sourceUrl||'');if(!info)throw new Error('GitHub Issue URLが不正です');return `https://api.github.com/repos/${encodeURIComponent(info.owner)}/${encodeURIComponent(info.repo)}/issues/${info.issue}/comments?per_page=100&page=${Math.max(1,Math.floor(Number(page)||1))}`}
async function fetchCustomIssuePage(r,page){const res=await fetch(customIssuePageUrl(r,page),{headers:{Accept:'application/vnd.github+json'},cache:'no-store'});if(!res.ok)throw new Error(`GitHub HTTP ${res.status}`);const data=await res.json();return{data:Array.isArray(data)?data:[],link:res.headers.get('link')||''}}
function parseGitHubIssueComment(c){const login=String(c?.user?.login||'GitHub'),body=String(c?.body||'').trim()||'(内容なし)',time=new Date(c?.created_at||Date.now()).toLocaleString('ja-JP',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});return['system',body,time,[],{commentId:String(c?.id||''),displayName:`@${login}`,role:'GitHub',avatar:'GH'}]}
function customMessageId(m){return String(m?.[4]?.commentId||'')}
function mergeCustomIssueComments(r,data,{prepend=false}={}){const parsed=(Array.isArray(data)?data:[]).map(parseGitHubIssueComment),existing=new Set(r.messages.map(customMessageId).filter(Boolean)),fresh=parsed.filter(m=>{const id=customMessageId(m);if(!id||existing.has(id))return false;existing.add(id);return true});if(prepend)r.messages=[...fresh,...r.messages];else{const byId=new Map(r.messages.map((m,i)=>[customMessageId(m),i]));for(const m of parsed){const id=customMessageId(m);if(id&&byId.has(id))r.messages[byId.get(id)]=m;else r.messages.push(m)}}return fresh.length}
async function loadOlderCustomIssue(ch){const r=rooms[ch];if(current!==ch||r?.type!=='custom'||!r.sourceUrl)return;const st=customSourceState(r);if(st.loading||st.loadingOlder||!st.initialized||!st.hasOlder)return;st.loadingOlder=true;const beforeHeight=feed.scrollHeight,beforeTop=feed.scrollTop;try{let data=[];if(st.olderBuffer.length){data=st.olderBuffer;st.olderBuffer=[]}else if(st.oldestPage>1){const page=st.oldestPage-1,result=await fetchCustomIssuePage(r,page);data=result.data;st.oldestPage=page}else{st.hasOlder=false;return}mergeCustomIssueComments(r,data,{prepend:true});st.hasOlder=st.olderBuffer.length>0||st.oldestPage>1;st.syncError='';saveState();if(current===ch&&!settingsOpen){render(true);requestAnimationFrame(()=>{feed.scrollTop=beforeTop+(feed.scrollHeight-beforeHeight);syncJumpBottom()})}}catch(e){st.syncError=e.message;console.warn('Older custom Issue load failed',e)}finally{st.loadingOlder=false;syncComposer()}}
async function loadCustomIssueChannel(ch,force=false){const r=rooms[ch];if(r?.type!=='custom'||!r.sourceUrl)return;const st=customSourceState(r);if(st.loading)return;if(!force&&Date.now()-st.lastFetch<30000&&st.initialized)return;st.loading=true;st.syncError='';if(current===ch&&!settingsOpen)render(true);try{if(!st.initialized){const first=await fetchCustomIssuePage(r,1),lastPage=progressLastPage(first.link);let latestData=[],oldestPage=lastPage;st.olderBuffer=[];if(lastPage===1){latestData=first.data;oldestPage=1}else{const newest=await fetchCustomIssuePage(r,lastPage);latestData=newest.data;if(newest.data.length<100){const prevPage=lastPage-1,prev=await fetchCustomIssuePage(r,prevPage),pair=[...prev.data,...newest.data],keep=Math.min(100,pair.length);st.olderBuffer=pair.slice(0,pair.length-keep);latestData=pair.slice(-keep);oldestPage=prevPage}}r.messages=latestData.map(parseGitHubIssueComment);st.newestPage=lastPage;st.oldestPage=oldestPage;st.hasOlder=st.olderBuffer.length>0||st.oldestPage>1;st.initialized=true}else{let page=st.newestPage,result=await fetchCustomIssuePage(r,page),batch=[...result.data],pageData=result.data;for(let i=0;i<5&&pageData.length===100;i++){const next=await fetchCustomIssuePage(r,page+1);if(!next.data.length)break;page++;pageData=next.data;batch.push(...pageData)}st.newestPage=page;const added=mergeCustomIssueComments(r,batch);if(added&&!isChannelVisibleAtBottom(ch)){unreadCounts[ch]=(unreadCounts[ch]||0)+added;renderChannelNav()}}st.lastFetch=Date.now();st.syncError='';saveState()}catch(e){st.syncError=e.message;console.warn('Custom GitHub Issue sync failed; keeping previous-good cache',e)}finally{st.loading=false;if(current===ch&&!settingsOpen)render(true);else syncComposer()}}
"""
replace_once(insert_before, custom_source_js + insert_before, 'custom source functions')

replace_once(
    "async function setChannel(ch){if(!rooms[ch])return;closeSettings();resetSearch();current=ch;saveState();closeDrawer();render();if(ch==='progress')await loadCanonicalProgress(true)}",
    "async function setChannel(ch){if(!rooms[ch])return;closeSettings();resetSearch();current=ch;saveState();closeDrawer();render();if(ch==='progress')await loadCanonicalProgress(true);else if(rooms[ch]?.type==='custom'&&rooms[ch]?.sourceUrl)await loadCustomIssueChannel(ch,false)}",
    'custom load on channel open',
)

replace_once(
    "function openChannelEditor(ch,{isNew=false}={}){if(!rooms[ch])return;editingMode='channel';editingChannel=ch;editingNewChannel=isNew;channelEditorTitle.textContent='チャンネルを編集';editorNameLabel.textContent='チャンネル名';editorDescLabel.textContent='説明';channelNameInput.maxLength=24;channelDescInput.maxLength=80;channelDescInput.placeholder='説明なし';channelNameInput.value=normalizedRoomName(ch);channelDescInput.value=rooms[ch].desc||'';showEditor()}",
    "function openChannelEditor(ch,{isNew=false}={}){if(!rooms[ch])return;editingMode='channel';editingChannel=ch;editingNewChannel=isNew;channelEditorTitle.textContent=isNew?'チャンネルを追加':'チャンネルを編集';editorNameLabel.textContent='チャンネル名';editorDescLabel.textContent='説明';channelNameInput.maxLength=24;channelDescInput.maxLength=80;channelDescInput.placeholder='説明なし';channelNameInput.value=normalizedRoomName(ch);channelDescInput.value=rooms[ch].desc||'';const isCustom=rooms[ch].type==='custom';channelSourceField.hidden=!isCustom;channelSourceInput.value=isCustom?(rooms[ch].sourceUrl||''):'';channelSourceError.textContent='';showEditor()}",
    'open custom source editor',
)

replace_once(
    "function openWorkspaceEditor(){closeSettings();closeDrawer();editingMode='workspace';editingChannel='';editingNewChannel=false;channelEditorTitle.textContent='ワークスペースを編集';editorNameLabel.textContent='ワークスペース名';editorDescLabel.textContent='サブタイトル';channelNameInput.maxLength=32;channelDescInput.maxLength=64;channelDescInput.placeholder='サブタイトルなし';channelNameInput.value=workspaceMeta.name;channelDescInput.value=workspaceMeta.sub;showEditor()}",
    "function openWorkspaceEditor(){closeSettings();closeDrawer();editingMode='workspace';editingChannel='';editingNewChannel=false;channelEditorTitle.textContent='ワークスペースを編集';editorNameLabel.textContent='ワークスペース名';editorDescLabel.textContent='サブタイトル';channelNameInput.maxLength=32;channelDescInput.maxLength=64;channelDescInput.placeholder='サブタイトルなし';channelNameInput.value=workspaceMeta.name;channelDescInput.value=workspaceMeta.sub;channelSourceField.hidden=true;channelSourceInput.value='';channelSourceError.textContent='';showEditor()}",
    'hide source for workspace',
)

replace_once(
    "function closeChannelEditor({discardNew=false}={}){if(editingMode==='channel'&&discardNew&&editingNewChannel&&rooms[editingChannel]?.type==='custom'){delete rooms[editingChannel];if(current===editingChannel)current='chat';saveState();render()}editingMode='channel';editingChannel='';editingNewChannel=false;channelEditorBackdrop.classList.remove('open');channelEditorBackdrop.setAttribute('aria-hidden','true')}",
    "function closeChannelEditor({discardNew=false}={}){if(editingMode==='channel'&&discardNew&&editingNewChannel&&rooms[editingChannel]?.type==='custom'){delete rooms[editingChannel];if(current===editingChannel)current='chat';saveState();render()}editingMode='channel';editingChannel='';editingNewChannel=false;channelSourceField.hidden=true;channelSourceInput.value='';channelSourceError.textContent='';channelEditorBackdrop.classList.remove('open');channelEditorBackdrop.setAttribute('aria-hidden','true')}",
    'close source editor',
)

replace_once(
    "function saveChannelEditor(){if(editingMode==='workspace'){workspaceMeta.name=String(channelNameInput.value||'').trim().slice(0,32)||'AI開発部';workspaceMeta.sub=String(channelDescInput.value||'').trim().slice(0,64);saveState();closeChannelEditor();syncWorkspaceLabels();return}if(!editingChannel||!rooms[editingChannel])return;rooms[editingChannel].name=String(channelNameInput.value||'').replace(/^#+\\s*/,'').trim().slice(0,24)||DEFAULT_ROOM_NAMES[editingChannel]||'Channel';rooms[editingChannel].desc=String(channelDescInput.value||'').trim().slice(0,80);saveState();closeChannelEditor();render()}",
    "function saveChannelEditor(){if(editingMode==='workspace'){workspaceMeta.name=String(channelNameInput.value||'').trim().slice(0,32)||'AI開発部';workspaceMeta.sub=String(channelDescInput.value||'').trim().slice(0,64);saveState();closeChannelEditor();syncWorkspaceLabels();return}if(!editingChannel||!rooms[editingChannel])return;const ch=editingChannel,r=rooms[ch];if(r.type==='custom'){const info=parseGitHubIssueUrl(channelSourceInput.value);if(!info){channelSourceError.textContent='https://github.com/owner/repo/issues/123 形式の公開Issue URLを入力してください。';channelSourceInput.focus();return}const sourceChanged=(r.sourceUrl||'')!==info.url;r.sourceUrl=info.url;r.rule='GitHub Issueのコメントを読み取り専用で同期します。';if(sourceChanged){r.messages=[];resetCustomSourceState(r)}}r.name=String(channelNameInput.value||'').replace(/^#+\\s*/,'').trim().slice(0,24)||DEFAULT_ROOM_NAMES[ch]||'Channel';r.desc=String(channelDescInput.value||'').trim().slice(0,80);saveState();closeChannelEditor();render();if(r.type==='custom'&&r.sourceUrl)loadCustomIssueChannel(ch,true)}",
    'save custom source',
)

replace_once(
    "rooms[id]={name:'新しいチャンネル',desc:'',type:'custom',placeholder:'読み取り専用',rule:'このチャンネルは読み取り専用です。',messages:[]};",
    "rooms[id]={name:'新しいチャンネル',desc:'',type:'custom',placeholder:'読み取り専用',rule:'GitHub Issueのコメントを読み取り専用で同期します。',messages:[],sourceUrl:''};",
    'new custom source model',
)

replace_once(
    "channelDescInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();saveChannelEditor()}else if(e.key==='Escape'){e.preventDefault();closeChannelEditor({discardNew:true})}});",
    "channelDescInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();saveChannelEditor()}else if(e.key==='Escape'){e.preventDefault();closeChannelEditor({discardNew:true})}});channelSourceInput.addEventListener('input',()=>{channelSourceError.textContent=''});channelSourceInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();saveChannelEditor()}else if(e.key==='Escape'){e.preventDefault();closeChannelEditor({discardNew:true})}});",
    'source editor events',
)

replace_once(
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===searchInput)",
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===channelSourceInput||e.target===searchInput)",
    'focusin source field',
)
replace_once(
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===searchInput){viewportLockUntil=Date.now()+900;",
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===channelSourceInput||e.target===searchInput){viewportLockUntil=Date.now()+900;",
    'focusout source field',
)

replace_once(
    "setInterval(()=>loadCanonicalProgress(true),300000);",
    "setInterval(()=>{loadCanonicalProgress(true);if(rooms[current]?.type==='custom'&&rooms[current]?.sourceUrl)loadCustomIssueChannel(current,true)},300000);",
    'active custom periodic sync',
)

path.write_text(text, encoding='utf-8')
