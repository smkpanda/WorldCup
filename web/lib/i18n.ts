export type Locale = "en" | "zh";

export function isLocale(value: string): value is Locale {
  return value === "en" || value === "zh";
}

export const copy = {
  en: {
    brand: "Match Forecast",
    predictions: "Predictions",
    review: "Post-match review",
    methodology: "Methodology",
    online: "Model online",
    disclaimer: "Entertainment forecast only. Not betting or investment advice.",
    tagline: "Read the match through data, not certainty.",
  },
  zh: {
    brand: "赛果先知",
    predictions: "比赛预测",
    review: "赛后复盘",
    methodology: "模型说明",
    online: "模型在线",
    disclaimer: "娱乐预测，不构成任何投注或投资建议。",
    tagline: "用数据读懂比赛，而不是预言未来。",
  },
} as const;

export function localTeam(team: { name: string; nameZh: string }, locale: Locale) {
  return locale === "zh" ? team.nameZh : team.name;
}

export function formatKickoff(iso: string, locale: Locale) {
  const date = new Date(iso);
  const language = locale === "zh" ? "zh-CN" : "en-US";
  const base = { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false } as const;
  const bjt = new Intl.DateTimeFormat(language, { ...base, timeZone: "Asia/Shanghai" }).format(date);
  const utc = new Intl.DateTimeFormat(language, { ...base, timeZone: "UTC" }).format(date);
  return { bjt: `${bjt} BJT (UTC+8)`, utc: `${utc} UTC` };
}
