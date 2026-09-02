# AI Dev Room — Workers AI backend

`#雑談` を本物のAI会話にするための無料枠向けCloudflare Workerです。

## 設計

- 1回のユーザー投稿につきWorkers AIは原則1回だけ呼ぶ
- 1推論で、反応するAIを1〜3人選び、その全員分の返信をまとめて返す
- `#進捗` はAI推論を使わず、事実ログとして扱う
- モデル: `@cf/zai-org/glm-4.7-flash`
- APIキーをGitHub Pagesへ置かない。Workers AI binding (`env.AI`) を使う

## API

### `GET /health`

Workerの稼働確認。

### `POST /chat`

```json
{
  "channel": "chat",
  "message": "Codex枯れたな",
  "history": [
    {"speaker":"あなた","text":"今日は何する？"},
    {"speaker":"Phase統括","text":"設計を先に詰めよう"}
  ]
}
```

レスポンス例:

```json
{
  "replies": [
    {"agent":"accounting","text":"今日は通常チャット寄りでいこ。"},
    {"agent":"manager","text":"実装は回復後でええな。"}
  ]
}
```

## Deploy

Cloudflare側でこの `worker` ディレクトリをWorkerとしてデプロイし、Workers AI binding `AI` を有効にします。

公開後の `*.workers.dev` URLをフロント側のAPI URLとして設定します。
