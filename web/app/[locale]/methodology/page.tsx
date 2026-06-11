import { notFound } from "next/navigation";
import { isLocale } from "@/lib/i18n";

const content = {
  en: {
    title: "How the model reads a match",
    lead: "A forecast is not a result. It converts information available before kickoff into calibrated probabilities.",
    sections: [
      ["Standardise player form", "Every metric is converted to a per-90 rate and scored by position. The last 30, 90 and 365 days receive different recency weights."],
      ["Adjust competition strength", "Club and international data are calculated separately and adjusted for competition and opponent strength."],
      ["Build team strength", "Expected starters receive the main weight, substitutes represent depth, and rankings, rest and tournament context are added."],
      ["Generate score probabilities", "Expected goals feed a Poisson score matrix. The displayed score is only the single most likely cell, not a certain outcome."],
    ],
    note: "Entertainment forecast only",
    disclaimer: "Injuries, confirmed lineups, red cards, penalties and other random events can materially change a match.",
  },
  zh: {
    title: "模型如何理解一场比赛",
    lead: "预测不是结果，而是把开赛前可用的信息转换为经过校准的概率。",
    sections: [
      ["标准化球员表现", "所有数据换算为每90分钟指标，并按位置评分。近30、90、365天采用不同时间权重。"],
      ["校正比赛强度", "俱乐部和国家队数据分别计算，并根据赛事等级和对手强度修正。"],
      ["构建球队能力", "预计首发承担主要权重，替补反映阵容深度，再加入排名、休息和赛事环境。"],
      ["生成比分概率", "预期进球进入泊松比分矩阵。展示比分只是概率最高的单一格子，并不是确定结果。"],
    ],
    note: "仅供娱乐预测",
    disclaimer: "伤停、正式首发、红牌、点球和其他随机事件都可能显著改变比赛。",
  },
} as const;

export default async function Methodology({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const text = content[locale];
  return (
    <main className="text-page">
      <span className="eyebrow">MODEL METHODOLOGY</span><h1>{text.title}</h1><p className="lead">{text.lead}</p>
      <div className="article-grid">{text.sections.map((section, index) => <section key={section[0]}><b>0{index + 1}</b><h2>{section[0]}</h2><p>{section[1]}</p></section>)}</div>
      <div className="disclaimer"><strong>{text.note}</strong><p>{text.disclaimer}</p></div>
    </main>
  );
}
