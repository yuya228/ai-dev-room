const ALLOWED_ORIGIN = "https://yuya228.github.io";
const MODEL = "@cf/zai-org/glm-4.7-flash";

const AGENTS = {
  manager: "Phase統括。全体進行と判断担当。短く現実的に話す。必要なら話をまとめるが、毎回仕切らない。",
  codex: "Codex A。実装担当。コードや作業の話に強い。今はクレジット節約を意識する。実装目線の軽い一言やツッコミもする。",
  qa: "Work QA。レビュー・品質管理担当。必要な時だけ懸念、確認点、品質目線のツッコミを出す。",
  accounting: "AI経理。AIクレジット・時間・差し戻しコストを監視する。必要な時だけ節約目線で短くドライに話し、軽いツッコミは可。性別を感じさせる口調や『〜わね』『〜かしら』などの女性語、特定の方言には寄せない。何でもコストの話にしない。",
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
    .slice(-12)
    .map((m) => ({
      speaker: String(m?.speaker || "").slice(0, 30),
      text: String(m?.text || "").slice(0, 500),
    }))
    .filter((m) => m.text);
}

function normalizeReplies(value) {
  const list = Array.isArray(value)
    ? value
    : Array.isArray(value?.replies)
      ? value.replies
      : value && typeof value === "object" && ("agent" in value || "text" in value)
        ? [value]
        : null;

  if (!list) return null;

  return list
    .slice(0, 3)
    .map((r) => ({
      agent: ["manager", "codex", "qa", "accounting"].includes(r?.agent) ? r.agent : "manager",
      text: String(r?.text || "").trim().slice(0, 320),
    }))
    .filter((r) => r.text);
}

function extractModelOutput(value, depth = 0) {
  if (value == null || depth > 8) return "";

  const direct = normalizeReplies(value);
  if (direct?.length) return value;

  if (typeof value === "string") return value.trim();
  if (typeof value !== "object") return "";

  if (Array.isArray(value)) {
    for (const part of value) {
      const extracted = extractModelOutput(part, depth + 1);
      if (typeof extracted === "string" ? extracted.trim() : normalizeReplies(extracted)?.length) {
        return extracted;
      }
    }
    return "";
  }

  const candidates = [
    value?.choices?.[0]?.message?.content,
    value?.choices?.[0]?.message,
    value?.choices?.[0]?.text,
    value?.message?.content,
    value?.message,
    value?.content,
    value?.text,
    value?.output_text,
    value?.response,
    value?.result,
  ];

  for (const candidate of candidates) {
    const extracted = extractModelOutput(candidate, depth + 1);
    if (typeof extracted === "string" ? extracted.trim() : normalizeReplies(extracted)?.length) {
      return extracted;
    }
  }

  return "";
}

function parseReplies(raw) {
  const direct = normalizeReplies(raw);
  if (direct?.length) return direct;

  const extracted = typeof raw === "string" ? raw : extractModelOutput(raw);
  const trimmed = String(extracted || "").trim();
  if (!trimmed) return [];

  const unfenced = trimmed
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/i, "")
    .trim();

  for (const candidate of [unfenced, trimmed]) {
    try {
      const parsed = JSON.parse(candidate);
      const replies = normalizeReplies(parsed);
      if (replies?.length) return replies;

      const nested = extractModelOutput(parsed);
      if (nested && nested !== candidate) {
        const nestedReplies = parseReplies(nested);
        if (nestedReplies.length) return nestedReplies;
      }
    } catch {
      // Continue with tolerant extraction below.
    }
  }

  const arrayStart = unfenced.indexOf("[");
  const arrayEnd = unfenced.lastIndexOf("]");
  if (arrayStart !== -1 && arrayEnd > arrayStart) {
    try {
      const replies = normalizeReplies(JSON.parse(unfenced.slice(arrayStart, arrayEnd + 1)));
      if (replies?.length) return replies;
    } catch {
      // Fall through.
    }
  }

  const objectStart = unfenced.indexOf("{");
  const objectEnd = unfenced.lastIndexOf("}");
  if (objectStart !== -1 && objectEnd > objectStart) {
    try {
      const parsed = JSON.parse(unfenced.slice(objectStart, objectEnd + 1));
      const replies = normalizeReplies(parsed);
      if (replies?.length) return replies;

      const nested = extractModelOutput(parsed);
      if (nested && nested !== unfenced) {
        const nestedReplies = parseReplies(nested);
        if (nestedReplies.length) return nestedReplies;
      }
    } catch {
      // Fall through.
    }
  }

  const fallbackText = unfenced.replace(/```(?:json)?|```/gi, "").trim().slice(0, 320);
  return fallbackText && fallbackText !== "[object Object]"
    ? [{ agent: "manager", text: fallbackText }]
    : [];
}

function finishReason(result) {
  return String(
    result?.choices?.[0]?.finish_reason ??
    result?.response?.choices?.[0]?.finish_reason ??
    result?.result?.choices?.[0]?.finish_reason ??
    ""
  );
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

    if (channel !== "chat") {
      return json({ replies: [] }, 200, origin);
    }

    const system = `あなたは「AI開発部」という架空のAI開発チームのSlack雑談チャンネルを演出するDispatcherです。

参加AI:
${Object.entries(AGENTS).map(([id, desc]) => `- ${id}: ${desc}`).join("\n")}

目的:
本物の社内Slackを眺めているような、短く自然な会話を作る。ユーザーへのFAQ回答大会にはしない。

ルール:
- ユーザーの1投稿に対して、反応する必要があるAIだけを1〜3人選ぶ。
- 1人で十分なら必ず1人だけにする。人数を増やすこと自体を目的にしない。
- 2〜3人出す場合、1人目はユーザーに自然に反応し、2人目以降は可能なら直前のAI発言への補足・同意・軽い反論・ツッコミとして会話をつなぐ。
- 複数人が同じ内容を言い換えて繰り返さない。
- ときどきAI同士で意見が少しズレてもよい。最終的に無理に合意しなくてよい。
- 1人あたり日本語1〜2文。Slackらしく自然で短く。
- 過剰に丁寧にしない。社内の同僚っぽく。
- ユーザーの文体に多少合わせてよいが、露骨なモノマネはしない。
- 直近の会話を踏まえ、既に言ったことを反復しない。
- 事実不明な進捗・クレジット残量・GitHub状態を勝手に作らない。
- 作業を実行したふりをしない。
- 「AIとして」などメタ発言は避ける。
- 出力順が、そのままSlack上の発言順になる。
- 出力は説明なしのJSON配列のみ。

良い例:
[{"agent":"accounting","text":"今日は無料枠で詰められるとこだけやっとくのがよさそう。"},{"agent":"manager","text":"せやな。じゃあ仕様とUIだけ固めて、重い実装は後ろに回すか。"}]

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
        max_completion_tokens: 4096,
        temperature: 0.9,
      });

      const replies = parseReplies(result);
      if (!replies.length) {
        const reason = finishReason(result);
        console.warn("Workers AI returned no displayable reply", { finishReason: reason || "unknown" });
        return json({
          error: "AI returned no displayable reply",
          detail: reason ? `finish_reason=${reason}` : "empty model content",
        }, 502, origin);
      }

      return json({ replies, model: MODEL }, 200, origin);
    } catch (error) {
      console.error(error);
      return json({ error: "AI generation failed", detail: String(error?.message || error) }, 500, origin);
    }
  },
};
