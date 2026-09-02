# AI Dev Slack v0.1

Slack風の「AI開発部」UIプロトタイプです。

## 特徴
- 完全静的HTML 1ファイル
- GitHub Pagesでそのまま公開可能
- チャンネル切替
- 人間からの投稿
- ローカルデモ用AI返信
- localStorageで会話保持
- Agent status / Phase progress / AI経理表示
- PC / iPhone対応
- 外部API・Codexクレジット消費なし

## GitHub Pagesへの置き方
1. 新しいGitHub repositoryを作成
2. `index.html` をrepository直下へアップロード
3. Settings → Pages
4. Deploy from a branch を選択
5. Branchを `main` / root に設定

## v0.2候補
- GitHub commit / PR / Issueを自動投稿
- Agentごとの実データ接続
- WebSocket / Supabase等でリアルタイム同期
- 「雑談」と「実作業依頼」の権限分離
- AI経理の実クレジットログ連携
