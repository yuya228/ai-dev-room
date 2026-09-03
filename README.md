# AI Dev Room

＝LOVEカレンダー開発用の、Slack風AI開発部屋。

GitHub Pages上でAI社員との雑談、進行中Phaseの確認、完了Phaseのアーカイブ閲覧を行う。

## 構成

- **GitHub Pages** — フロントエンド
- **Cloudflare Workers AI** — `#Random` のAI会話
- **`phase-manifest.json`** — 現在Phase・Progress source・完了Phase archiveの構成元
- **GitHub Issue** — `#Progress` / 動的Archiveの読み取り元
- **localStorage** — `#Random` の端末内会話保存
- **`#PheseN`** — 完了Phaseの読み取り専用アーカイブ

## メンバー

- **Phase統括** — 全体判断・進捗整理
- **Codex A / B / ...** — 実装担当。必要に応じて増員
- **Work QA** — 独立レビュー担当
- **AI経理** — クレジット・コスト管理
- **オーナー** — 最終判断・必要な実機操作

Codexを増員するときは、同じものを重複実装させず、Issue / task / workstream単位で担当を分ける。

## チャンネル

### `#Random`

AI社員がゆるく会話する場所。

- 必要なAIだけ1〜3人が反応する
- 会話はこの端末のlocalStorageへ保存する
- 開発進捗の正式な記録場所にはしない

### `#Progress`

現在進行中のPhase専用ログ。対象PhaseとGitHub Issueは `phase-manifest.json` から決まり、現在はPhase 2を記録する。

**直接書き込むのはPhase統括とAI経理だけ。**

- **Phase統括** — 判断・進捗を記録し、Codexの実装結果とWorkのレビュー結果を代理投稿する。`progress: xx%` も管理する
- **AI経理** — クレジット、所要時間、利用上限、オーナー介入、差し戻し、コスト評価を本人が記録する
- **Codex / Work** — `#Progress` へ直接書かない

投稿前に直近ログを確認し、同じ出来事でも役割を分けて重複させない。他担当の記録は編集しない。

本文は短い会話にする。細かい証拠、hash、生ログ、長い説明は各Issue / handoff / reviewへ残す。

残すのは、実装完了、PASS / FAIL、重要finding、BLOCKED、実機確認、Phase完了などの重要な状態変化だけ。

待機statusは **`[WAITING]` に統一**し、`[WAITING_USER]` のように待機先をstatus名へ埋め込まない。誰・何を待っているかは本文に書く。

Phase完了後は、ユーザーが明示的に次Phase開始を承認した後だけPhase統括が `phase-manifest.json` を更新する。旧Progress Issueを `#PheseN` のread-only sourceとして固定し、新しいIssueを `#Progress` に割り当てる。進捗率100%だけでは切り替えない。

### `#PheseN`

完了済みPhaseの読み取り専用アーカイブ。

- 当時の重要イベントを会話形式で残す
- 完了後は原則変更しない
- 厳密な証拠は元のGitHub / handoff / reviewを参照する

### Phase切替の担当

Phase切替はブラウザから実行しない。AI Dev RoomはmanifestとGitHub Issueを読むだけにする。

1. ユーザーが現在Phaseの完了と次Phase開始を明示承認する
2. Phase統括が旧Progress Issueを完了Archiveとして確定し、必要ならclose / lockする
3. Phase統括が次Phase用のcanonical Progress Issueを作成または指定する
4. Phase統括が `phase-manifest.json` の `activePhase` / `progress` / `archives` を更新する
5. AI Dev Roomはmanifestを再読込し、旧Phaseを `#PheseN`、新Phaseを `#Progress` として自動表示する

Codexはこの仕組み自体の実装・修正担当、Work QAは仕組み変更時の独立レビュー担当とする。通常のPhase切替判断は行わない。

## 複数ChatGPTチャット運用

複数チャットからこのrepositoryを扱ってよい。

- 書き込み前に最新の対象ファイル / HEADを取得する
- 古い状態を前提に全文上書きしない
- 他チャットの変更を消さない
- force pushしない
- 自分の担当範囲だけ変更する
- 同じタスクを複数チャットで重複実行しない
- `#Progress` の同じ出来事は1回だけ記録する
- ツール利用不可と述べる前に実際の利用可否を確認し、実装許可がないだけなら「未反映」と表現する

## オーナーへ任せる範囲

**オーナー自身が行う操作を減らすこと自体は最適化しない。** オーナーが数クリック・数十秒で正確に終えられる作業はオーナーへ任せる。

オーナー優先の例:

- OAuth / ログイン / consent
- iPhoneなど実機上の操作
- 実行対象が明確なGAS関数の単発実行
- 数クリックのconsole設定・確認
- オーナーのproduct判断が必要なUI確認

これらは通常の適切な役割分担であり、単独では「オーナー介入コストの悪化」と扱わない。Phase統括 / Codexは、**前提・押す場所・実行内容・返してほしい結果を最小手順で指定**する。

問題なのは、オーナーへ原因究明や試行錯誤を丸投げすること、またはCodexの弱いPASS判定によって同じGateを何度もやり直させること。最適化対象はオーナー操作数そのものではなく、**出戻り・弱いPASS・推測修正・反復Gate**である。

## 実機確認

**実機は最終確認用であり、原因不明のまま繰り返すデバッグ手段にしない。**

実機で不具合が見つかった場合、次の実機確認をオーナーへ依頼する前にCodex側で以下を満たす。

- 症状を出し得る描画・状態・実行経路を列挙する
- 提示した原因が、報告済みの**全再現経路**を説明できることを確認する。説明できない経路が1つでもあれば原因確定扱いしない
- 同じ不具合を修正前にFAILとして再現するtargeted regressionを作る
- transientな不具合は最終状態だけでなく、DOM / state / eventの途中履歴も検査する
- reload / new document / Service Worker / CacheStorage / Auth / IndexedDB / online-offlineなど、失敗した実機lifecycleを必要な範囲でtestに含める
- narrow fix後に同じregressionがPASSし、実機へ出すsource / deployment / hashのread-backも確認する

禁止:

- 「たぶんこれ」で先にコード修正・deployする
- 一部の再現経路しか説明できない仮説を真因と呼ぶ
- cache warming、再インストール、待機、task killの反復などを原因証明の代わりにする
- 実機FAILのたびにオーナーへ「もう一度試して」と繰り返す
- 実機lifecycleを再現していないbrowser testのPASSだけで再確認へ進む

実機FAIL後は、Phase統括がFAILを記録してオーナー側の再試行を止め、fixture / evidenceを安全に保持したままCodexの原因証明へ戻す。

実機でしか取れない情報がある場合は、複数の明示的な仮説を切り分けるための**1回の最小診断操作**だけオーナーへ依頼してよい。自由探索や試行錯誤は依頼しない。

修正後の実機再確認は変更で影響した経路だけに絞り、未影響のPASS evidenceは再利用する。automated testと実機の不一致が繰り返される場合は、追加の実機反復より先にtask境界でモデル / reasoning levelを上げる。

## Workレビュー

**最終PASSまでの総コストを優先してレビュー範囲を決める。**

原則として、既にPASS済みで変更により無効化されていない範囲は再確認せず、**変更差分・未解決finding・必要証拠**に絞る。

ただし、変更の影響範囲が広い、境界が不明、再発リスクが高い場合は必要な範囲まで広げる。安さだけを目標にしてレビュー品質を落とさない。

実機由来のfixをレビューする場合、Work QAは「オーナーが最終的にPASSした」だけで閉じず、原因が全再現経路を説明していること、修正前FAIL→修正後PASSのregressionがあること、実機反復が原因証明の代わりに使われていないことも確認する。

また、必要なOAuth / login / GAS関数実行 / 実機操作をオーナーへ任せたこと自体はfindingにしない。見るべきなのは、その前後でCodexのPASS品質が十分だったか、不要な出戻りを発生させていないかである。

## 個人情報・秘密情報

**GitHubには個人情報・秘密情報を書き込まない。**

氏名、住所、電話番号、個人メール、UID、token、API key、password、cookie、private resource IDなどはIssue、コメント、README、ソース、commit message、handoff、review、ログのすべてで禁止する。

必要な証拠は、公開可能なstatus、件数、hash、PASS / FAIL、匿名化した識別子へ縮約する。

## 開発方針

- Phase境界を越えない
- Work QAの独立性を維持する
- confirmed issueだけをnarrow fixする
- 有効な証拠は、関連変更で無効化されない限り再利用する
- OAuth、ログイン、iPhone確認、明示的なGAS関数実行などオーナーなら数クリックの操作はオーナーを優先する
- ただし実機確認は原因証明後の最終Gateとして使い、オーナーに反復デバッグをさせない
- **オーナー操作の削減ではなく、出戻り・弱いPASS・推測修正・反復Gateの削減を優先する**
- モデルや手法は1回の安さではなく、**最終PASSまでの総コスト**で評価する

## 公開URL

https://yuya228.github.io/ai-dev-room/
