# AI開発運用体制 v0.3

## Purpose

＝LOVEカレンダー開発で、品質を維持しながらCodexのクレジット消費と不要な試行錯誤を減らすための役割分担を定義する。

本書はP4-B以降の標準運用とする。P4-Aは開始済みのため、現行運用のままclosureまで進める。

## Role model

### Phase統括

- Phase / checkpointの開始・終了判断
- scope、fixed base、Source of Truth、STOP条件の固定
- 担当振り分けと進捗管理
- Dev Roomの`#Progress`更新
- 次Phase / checkpointへの無断着手を防止する

### Codex Sol

Dev Roomや進捗上では、以下の2工程をまとめて従来どおり **Codex Sol** と扱う。

1. **Chat開発用Sol**
   - SOT読解
   - current canonical codeの必要範囲確認
   - 曖昧点・仕様判断点の洗い出し
   - 実装設計
   - 変更箇所の特定
   - 実装コード作成
   - 可能ならそのまま適用できるpatch / diff / replacement code作成
   - tests / failure injection / 検証手順 / STOP条件の作成
   - Codexへ渡すnarrow implementation briefの完成

2. **Codex実作業**
   - 指定されたコード / patchの反映
   - 必要最小限のSOTで一意に決まる調整
   - 指定test / failure injectionの実行
   - read-back / hash / HEAD確認
   - temporary helperの実行とcleanup
   - handoff作成
   - commit / push / remote delivery

基本原則は **Codexに広く考えさせず、Chat開発用Solで決めたものを正確に実行させる** こと。Codexへ渡す前に、可能な限り「どのファイルのどこをどう変えるか」「何をtestするか」「何をもってPASSか」まで固定する。

Codex側での広範囲探索、SOTの再読解、仕様の再発明、目的のない全体regressionは原則行わない。

### Codex Astra

通常ルートには使用しない。以下のような高難度taskだけ、Phase統括判断でスポット利用する。

- Solでは収束しない複雑なrecovery / concurrency / security設計
- 原因特定が難しい複合bug
- 広い影響分析が避けられないtask
- automated evidenceと実機挙動が繰り返し矛盾し、reasoning levelを上げる必要がある場合

Astraを使う場合もscopeを狭くし、結果をCodex Solの実装ブリーフへ戻す。Astraを通常実装担当として常用しない。

### Codex Luna

- docs / handoff / 命名 / ファイル整理などの低リスク作業
- コードロジック変更や仕様判断は原則担当しない

### Work QA

- Codex Sol / Astraから独立したQA担当
- accepted evidenceを再利用し、変更差分・未解決finding・必要証拠に絞ってレビューする
- コード修正が必要ならnarrow fixを要求する
- 文書・証拠整理だけで閉じられるfindingを不要にコード修正へ広げない

### Owner

AIに任せるより速く、安く、安全な短いaccount-bound操作を担当する。

Owner優先:
- OAuth / login / consent
- iPhoneなど実機操作
- 実行対象が明確なApps Script関数の単発実行
- 数クリックで終わるWeb / console設定・確認
- product判断を伴うUI確認

Phase統括 / Codex Solは、Ownerへ渡す場合に前提・押す場所・実行内容・返してほしい結果だけを最小手順で示す。単純なブラウザ操作をCodexへ回してクレジットを消費しない。

### AI経理

- クレジット、時間、利用上限、差し戻し、Owner作業、コスト評価を記録する
- AI経理の記録はAI経理本人が行い、Phase統括は代理投稿しない

## Standard flow

P4-B以降の標準フロー:

`Phase統括 → Chat開発用Sol → Codex実作業 → Work QA → Phase統括 closure`

1. Phase統括がscope / dependency / fixed baseを固定する
2. Chat開発用Solが設計・曖昧点整理・実装コード・test設計まで可能な限り完成させる
3. Codexはnarrow briefどおりに反映・検証・commit/push・remote read-backを行う
4. Work QAが独立レビューする
5. findingがあればChat開発用Solで必要な判断を先に詰め、Codexはnarrow fixだけ行う
6. Work PASS後にPhase統括がcheckpoint closure / 次工程を判断する

高難度で通常ルートが収束しない場合のみ、途中でAstraへ限定escalationする。

## Codex brief completion gate

Codexへ実作業を渡す前に、可能な範囲で以下を固定する。

- repository / branch / fixed base
- Source of Truthの参照範囲
- 対象action / 対象外scope
- 変更対象file / function / region
- 実装方針
- 適用するcode / patch / replacement
- targeted tests
- failure injection
- expected PASS criteria
- evidence reuse範囲
- Ownerへ回す短い操作
- STOP条件
- handoff / commit / push / remote read-back条件

このgateの目的は、Codexにrepository探索や仕様判断を再度させないこと。

## STOP policy

同一承認scope内のcode適用、targeted tests、failure injection、temporary helper、cleanup、read-back、hash、commit、push、remote deliveryは途中確認なしで完了まで進める。

STOPするのは次の場合だけ:
- SOTから決められない仕様判断
- 当初scopeを超える変更
- new OAuth consent
- IAM権限変更
- production dataへの影響
- 未承認のproduction / legacy環境変更
- destructive action whose safety cannot be established
- 次Phase / checkpointへの着手

Ownerが数クリックで済む操作が必要な場合は、AI側で長時間探索せずOwner向け最小手順へ切り替える。

## Dev Room representation

Dev Roomでは内部工程を細分化しすぎず、**Chat開発用Sol + Codex実作業をまとめて`Codex Sol`** として記録する。

- Chat開発用Solだけで設計・コード作成した場合も、実装task全体のactorはCodex Sol
- Codexがpatch適用・test・pushを実行した場合もCodex Sol
- Astraを実際に高難度taskへescalateした場合だけCodex Astra
- WorkはWork QA
- Phase判断はPhase統括
- コスト記録はAI経理本人

モデル名や内部ツール分担より、開発上の責任roleをactor名として優先する。

## Cost principle

1回の呼び出し単価ではなく **最終PASSまでの総コスト** を最適化する。ただし通常実装では、無料またはChat側で可能な設計・コード作成を先に行い、CodexクレジットはChatでは実行できない実作業へ集中させる。

優先順位:
1. Chatで設計・コード・test planを固める
2. Ownerが短時間でできるaccount-bound操作はOwnerへ回す
3. Codexは適用・実行・検証・deliveryに集中する
4. Workは独立QAを維持する
5. 高難度時だけAstraへ限定escalationする

品質を落としてクレジットだけを削る運用にはしない。