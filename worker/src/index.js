const ALLOWED_ORIGIN = "https://yuya228.github.io";
const MODEL = "@cf/zai-org/glm-4.7-flash";

const AGENTS = {
  manager: "Phase統括。全体進行と判断担当。短く現実的に話す。",
  codex: "Codex A。実装担当。コードや作業の話に強い。今はクレジット節約を意識する。",
  qa: "Work QA。レビュー・品質管理担当。必要な時だけ懸念や確認点を出す。",
  accounting: "AI経理。AIクレジット・時間・差し戻しコストを監視する。節約目線で軽くツッコむ。",
};

function corsHeaders(origin) {
  const allowed = origin === ALLOWED_ORIGIN || origin === "http://localhost:8787";
  return {
    "Access-Control-Allow-Origin": allowed ? origin : ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function json(data, status = 200, origin = ALLOWED_ORIGIN) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...corsHeaders(origin),
    },
  });
}

function cleanHistory(history) {
  if (!Array.isArray(history)) return [];
  return history
    .slice(-10)
    .map((m) => ({
      speaker: String(m?.speaker || "").slice(0, 30),
      text: String(m?.text || "").slice(0, 500),
    }))
    .filter((m) => m.text);
}

function parseReplies(text) {
  const trimmed = String(text || "").trim();
  const match = trimmed.match(/\[[\s\S]*\]/);
  if (!match) throw new Error("Model did not return a JSON array");
  const parsed = JSON.parse(match[0]);
  if (!Array.isArray(parsed)) throw new Error("Invalid reply format");

  return parsed
    .slice(0, 3)
    .map((r) => ({
      agent: ["manager", "codex", "qa", "accounting"].includes(r?.agent) ? r.agent : "manager",
      text: String(r?.text || "").trim().slice(0, 320),
    }))
    .filter((r) => r.text);
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || ALLOWED_ORIGIN;

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return json({ ok: true, model: MODEL }, 200, origin);
    }

    if (url.pathname !== "/chat" || request.method !== "POST") {
      return json({ error: "Not found" }, 404, origin);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "Invalid JSON" }, 400, origin);
    }

    const message = String(body?.message || "").trim().slice(0, 1000);
    const channel = body?.channel === "progress" ? "progress" : "chat";
    const history = cleanHistory(body?.history);

    if (!message) return json({ error: "message is required" }, 400, origin);

    // v0.2では本物のAI雑談は #雑談 だけ。#進捗 は事実ログとしてAI推論を使わない。
    if (channel !== "chat") {
      return json({ replies: [] }, 200, origin);
    }

    const system = `あなたは「＝LOVE開発部」という架空のAI開発チームのSlack雑談チャンネルを演出するDispatcherです。

参加AI:
${Object.entries(AGENTS).map(([id, desc]) => `- ${id}: ${desc}`).join("\n")}

ルール:
- ユーザーの1投稿に対して、反応する必要があるAIだけを1〜3人選ぶ。
- 全員を毎回喋らせない。
- AI同士で少し会話がつながってもよい。
- 1人あたり日本語1〜2文、Slackらしく自然で短く。
- 過剰に丁寧にしない。社内の同僚っぽく。
- 事実不明な進捗・クレジット残量・GitHub状態を勝手に作らない。
- 作業を実行したふりをしない。
- 「AIとして」などメタ発言は避ける。
- 出力は説明なしのJSON配列のみ。

出力形式:
[{"agent":"manager","text":"..."},{"agent":"accounting","text":"..."}]`;

    const context = history.length
      ? `直近の会話:\n${history.map((m) => `${m.speaker}: ${m.text}`).join("\n")}\n\nあなた: ${message}`
      : `あなた: ${message}`;

    try {
      const result = await env.AI.run(MODEL, {
        messages: [
          { role: "system", content: system },
          { role: "user", content: context },
        ],
        max_tokens: 320,
        temperature: 0.8,
      });

      const raw = result?.response ?? result?.result?.response ?? "";
      const replies = parseReplies(raw);
      return json({ replies, model: MODEL }, 200, origin);
    } catch (error) {
      console.error(error);
      return json({ error: "AI generation failed", detail: String(error?.message || error) }, 500, origin);
    }
  },
};
