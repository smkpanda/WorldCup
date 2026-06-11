import Link from "next/link";
import { formatKickoff, localTeam, type Locale } from "@/lib/i18n";
import type { Prediction } from "@/lib/types";

const t = {
  en: {
    worldRank: "World rank",
    modelPick: "Central score projection",
    confidence: "Data confidence",
    home: "Home",
    draw: "Draw",
    away: "Away",
    analysis: "Full analysis",
    hero: <>A clearer way<br />to <em>read the match</em></>,
    intro: "Team history, player form over the last year, squad quality and competition strength, converted into explainable probabilities.",
    window: "day player window",
    features: "core features",
    matrix: "score outcomes",
    focus: "Opening match",
    next: "Next forecast",
    updated: "Data updated",
    upcoming: "Upcoming",
    more: "More matches",
    steps: [
      ["Team baseline", "Rankings, recent results and tournament history"],
      ["Player form", "Position-specific performance per 90 minutes"],
      ["Squad context", "Lineup, injuries, schedule and rest"],
      ["Probability", "Poisson score matrix and outcome probabilities"],
    ],
  },
  zh: {
    worldRank: "世界排名",
    modelPick: "中心比分预测",
    confidence: "数据置信度",
    home: "主胜",
    draw: "平局",
    away: "客胜",
    analysis: "查看完整分析",
    hero: <>用数据<br /><em>读懂每一场比赛</em></>,
    intro: "结合国家队历史、球员近一年状态、阵容质量与赛事强度，用可解释概率拆解每一场对决。",
    window: "天球员数据窗口",
    features: "项核心比赛特征",
    matrix: "种比分结果",
    focus: "揭幕战",
    next: "下一场预测",
    updated: "数据更新",
    upcoming: "即将开赛",
    more: "更多比赛",
    steps: [
      ["球队底盘", "国际排名、近期战绩与历史大赛表现"],
      ["球员状态", "按位置分析每90分钟表现"],
      ["阵容情境", "首发、伤停、赛程强度与休息时间"],
      ["概率输出", "泊松比分矩阵与胜平负概率"],
    ],
  },
} as const;

function MatchCard({ match, locale, featured = false }: { match: Prediction; locale: Locale; featured?: boolean }) {
  const text = t[locale];
  const kickoff = formatKickoff(match.kickoff, locale);
  return (
    <article className={`match-card ${featured ? "featured" : ""}`}>
      <div className="card-topline">
        <span>{locale === "zh" ? match.stageZh : match.stage}</span>
        <time><b>{kickoff.bjt}</b><small>{kickoff.utc}</small></time>
      </div>
      <div className="teams">
        <div className="team"><span className="flag">{match.homeTeam.flag}</span><strong>{localTeam(match.homeTeam, locale)}</strong><small>{text.worldRank} #{match.homeTeam.fifaRank}</small></div>
        <div className="score-pick"><small>{text.modelPick}</small><b>{match.likelyScore}</b><span>{text.confidence} {match.confidence}%</span></div>
        <div className="team"><span className="flag">{match.awayTeam.flag}</span><strong>{localTeam(match.awayTeam, locale)}</strong><small>{text.worldRank} #{match.awayTeam.fifaRank}</small></div>
      </div>
      <div className="probability">
        <div className="prob-labels"><span><b>{match.homeWin}%</b> {text.home}</span><span><b>{match.draw}%</b> {text.draw}</span><span><b>{match.awayWin}%</b> {text.away}</span></div>
        <div className="prob-bar"><i style={{ width: `${match.homeWin}%` }} /><i style={{ width: `${match.draw}%` }} /><i style={{ width: `${match.awayWin}%` }} /></div>
        <div className="mini-scores">{match.topScores.map((score) => <span key={`${score.home}-${score.away}`}>{score.home}–{score.away} <b>{score.probability}%</b></span>)}</div>
      </div>
      <div className="card-footer"><span>{locale === "zh" ? match.venueZh : match.venue}</span><Link href={`/${locale}/matches/${match.id}`}>{text.analysis} <b>→</b></Link></div>
    </article>
  );
}

export default function HomePage({ predictions, locale }: { predictions: Prediction[]; locale: Locale }) {
  const text = t[locale];
  const upcoming = predictions.filter((match) => match.status === "upcoming").sort((a, b) => Date.parse(a.kickoff) - Date.parse(b.kickoff));
  const [featured, ...more] = upcoming;
  return (
    <main>
      <section className="hero">
        <div className="hero-copy"><span className="eyebrow">2026 FIFA WORLD CUP</span><h1>{text.hero}</h1><p>{text.intro}</p>
          <div className="hero-stats"><div><b>365</b><span>{text.window}</span></div><div><b>20+</b><span>{text.features}</span></div><div><b>64</b><span>{text.matrix}</span></div></div>
        </div>
        <div className="orb"><div className="orb-grid" /><div className="orb-center"><b>2026</b><span>WORLD CUP</span></div></div>
      </section>
      <section className="content-section">
        <div className="section-heading"><div><span className="eyebrow">{text.focus}</span><h2>{text.next}</h2></div><p>{text.updated}: {formatKickoff(featured.updatedAt, locale).utc}</p></div>
        <MatchCard match={featured} locale={locale} featured />
      </section>
      <section className="content-section">
        <div className="section-heading"><div><span className="eyebrow">{text.upcoming}</span><h2>{text.more}</h2></div></div>
        <div className="match-grid">{more.map((match) => <MatchCard key={match.id} match={match} locale={locale} />)}</div>
      </section>
      <section className="method-strip">{text.steps.map((step, index) => <div key={step[0]}><span>0{index + 1}</span><h3>{step[0]}</h3><p>{step[1]}</p></div>)}</section>
    </main>
  );
}
