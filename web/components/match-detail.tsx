import Link from "next/link";
import { formatKickoff, localTeam, type Locale } from "@/lib/i18n";
import type { Prediction } from "@/lib/types";

export default function MatchDetail({ match, locale }: { match: Prediction; locale: Locale }) {
  const zh = locale === "zh";
  const kickoff = formatKickoff(match.kickoff, locale);
  return (
    <main className="detail-page">
      <Link href={`/${locale}`} className="back-link">← {zh ? "返回比赛列表" : "Back to matches"}</Link>
      <section className="detail-hero">
        <div className="detail-meta">{zh ? match.stageZh : match.stage} · {zh ? match.venueZh : match.venue}<br />{kickoff.bjt} · {kickoff.utc}</div>
        <div className="detail-teams">
          <div><span className="flag xl">{match.homeTeam.flag}</span><h1>{localTeam(match.homeTeam, locale)}</h1><p>{zh ? "世界排名" : "World rank"} #{match.homeTeam.fifaRank}</p></div>
          <div className="detail-score"><small>{zh ? "中心比分预测" : "Central score projection"}</small><b>{match.likelyScore}</b><span>{match.expectedHomeGoals.toFixed(2)} xG · {match.expectedAwayGoals.toFixed(2)} xG</span></div>
          <div><span className="flag xl">{match.awayTeam.flag}</span><h1>{localTeam(match.awayTeam, locale)}</h1><p>{zh ? "世界排名" : "World rank"} #{match.awayTeam.fifaRank}</p></div>
        </div>
        <div className="detail-probs"><div><b>{match.homeWin}%</b><span>{localTeam(match.homeTeam, locale)} {zh ? "胜" : "win"}</span></div><div><b>{match.draw}%</b><span>{zh ? "平局" : "Draw"}</span></div><div><b>{match.awayWin}%</b><span>{localTeam(match.awayTeam, locale)} {zh ? "胜" : "win"}</span></div></div>
      </section>
      <div className="analysis-grid">
        <section className="panel"><div className="panel-title"><span>01</span><h2>{zh ? "关键影响因素" : "Key factors"}</h2></div>
          {match.factors.map((factor) => <div className="factor" key={factor.label}><div><strong>{zh ? factor.labelZh : factor.label}</strong><small>{zh ? factor.noteZh : factor.note}</small></div><div className="factor-values"><b>{factor.home}</b><i><span style={{ width: `${factor.home / (factor.home + factor.away) * 100}%` }} /></i><b>{factor.away}</b></div></div>)}
        </section>
        <section className="panel"><div className="panel-title"><span>02</span><h2>{zh ? "比分概率前三" : "Top score probabilities"}</h2></div><div className="score-list">
          {match.topScores.map((score, index) => <div key={`${score.home}-${score.away}`}><span>0{index + 1}</span><b>{score.home} – {score.away}</b><em>{score.probability.toFixed(1)}%</em></div>)}
        </div></section>
      </div>
      <section className="panel players-panel"><div className="panel-title"><span>03</span><h2>{zh ? "关键球员 · 近365天" : "Key players · last 365 days"}</h2></div><div className="player-table">
        <div className="table-row header"><span>{zh ? "球员" : "Player"}</span><span>{zh ? "位置" : "Position"}</span><span>{zh ? "进球" : "Goals"}</span><span>{zh ? "助攻" : "Assists"}</span><span>{zh ? "分钟" : "Minutes"}</span><span>{zh ? "状态评分" : "Form rating"}</span></div>
        {match.keyPlayers.map((player) => <div className="table-row" key={player.name}><strong>{player.name} <small>{player.teamCode}</small></strong><span>{zh ? player.positionZh : player.position}</span><b>{player.goals}</b><b>{player.assists}</b><span>{player.minutes.toLocaleString()}</span><em>{player.rating}</em></div>)}
      </div></section>
      <p className="trace">{zh ? "模型" : "Model"} {match.modelVersion} · {zh ? "数据版本" : "Data"} {match.dataVersion} · {zh ? "置信度" : "Confidence"} {match.confidence}%</p>
    </main>
  );
}
