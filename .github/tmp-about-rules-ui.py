from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = '''<div class="settings-backdrop" id="aboutRulesBackdrop" aria-hidden="true"><section class="settings-panel" aria-labelledby="aboutRulesTitle"><header class="settings-head"><button class="settings-mobile-menu" id="aboutRulesMobileMenu" aria-label="メニューを開く">☰</button><div><div class="settings-title" id="aboutRulesTitle">About / Rules</div><div class="settings-sub">プライバシー・運用ルール</div></div></header><div class="settings-scroll"><div class="settings-body"><section class="settings-group"><div><div class="settings-rule-row"><strong>プライバシー</strong><span class="danger-copy">GitHubに個人情報・認証情報・秘密情報を書き込まない。</span></div><div class="settings-rule-row"><strong>複数チャット運用</strong><span>書き込み直前に最新状態を確認し、他チャットの変更を消さない。</span></div><div class="settings-rule-row"><strong>AI開発ルール</strong><span>Phase境界、narrow fix、Work QAの独立性、最終PASSまでの総コストを優先する。</span></div><div class="settings-rule-row"><strong>Random</strong><span>Workers AIが必要なAIだけ1〜3人選んで反応。複数人ならAI同士でも会話をつなぐ。作業実行はしない。</span></div></div></section></div></div></section></div>'''

new = '''<div class="settings-backdrop" id="aboutRulesBackdrop" aria-hidden="true"><section class="settings-panel" aria-labelledby="aboutRulesTitle"><header class="settings-head"><button class="settings-mobile-menu" id="aboutRulesMobileMenu" aria-label="メニューを開く">☰</button><div><div class="settings-title" id="aboutRulesTitle">About / Rules</div><div class="settings-sub">プライバシー・運用ルール</div></div></header><div class="settings-scroll"><div class="settings-body"><section class="settings-group"><div><div class="settings-rule-row"><strong>プライバシー</strong><span class="danger-copy">GitHubには公開可能な情報だけを書く。個人情報・認証情報・秘密情報は禁止。</span></div><div class="settings-rule-row"><strong>複数チャット運用</strong><span>書き込み直前に最新状態を確認し、重複投稿や他チャットの変更上書きをしない。</span></div><div class="settings-rule-row"><strong>Issue運用</strong><span>1コメント＝1つの重要な状態変化。ヘッダーは [時刻] [actor: 役割] [STATUS] の3ブラケット固定。本文はプレーンテキスト。recorded_by は使わない。進捗率はPhase統括の NEXT でだけ更新する。</span></div><div class="settings-rule-row"><strong>START</strong><span>対象作業を開始。</span></div><div class="settings-rule-row"><strong>NEXT</strong><span>Phase統括が次の作業・進行先を決定。必要ならここで進捗率を更新。</span></div><div class="settings-rule-row"><strong>PASS</strong><span>検証・レビュー成功。</span></div><div class="settings-rule-row"><strong>FAIL</strong><span>検証・レビュー失敗。</span></div><div class="settings-rule-row"><strong>FIX</strong><span>confirmed findingへの修正完了。</span></div><div class="settings-rule-row"><strong>BLOCKED</strong><span>問題があり先へ進めない。</span></div><div class="settings-rule-row"><strong>WAITING</strong><span>外部確認・入力など待機中。何待ちかは本文に書く。</span></div><div class="settings-rule-row"><strong>CLOSED</strong><span>対象の完了条件を満たして終了。</span></div><div class="settings-rule-row"><strong>COST</strong><span>AI経理によるクレジット・時間・コスト記録。</span></div><div class="settings-rule-row"><strong>AI開発ルール</strong><span>Phase境界、narrow fix、Work QAの独立性、最終PASSまでの総コストを優先する。次Phaseはオーナーの明示承認後のみ開始する。</span></div><div class="settings-rule-row"><strong>Random</strong><span>Workers AIが必要なAIだけ1〜3人選んで反応。複数人ならAI同士でも会話をつなぐ。作業実行はしない。</span></div></div></section></div></div></section></div>'''

count = text.count(old)
if count != 1:
    raise SystemExit(f'expected one About / Rules target, found {count}')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')

checks = [
    '1コメント＝1つの重要な状態変化。',
    '<strong>NEXT</strong>',
    '進捗率はPhase統括の NEXT でだけ更新する。',
    'recorded_by は使わない。',
    '次Phaseはオーナーの明示承認後のみ開始する。',
]
for marker in checks:
    if text.count(marker) != 1:
        raise SystemExit(f'marker count mismatch: {marker!r} -> {text.count(marker)}')

if '書き込み直前に最新状態を確認し、他チャットの変更を消さない。' in text:
    raise SystemExit('old About / Rules copy remains')
