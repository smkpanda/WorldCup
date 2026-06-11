import { formatKickoff, localTeam, type Locale } from "@/lib/i18n";
import type { Prediction } from "@/lib/types";

export default function ReviewPageView({ matches, locale }: { matches: Prediction[]; locale: Locale }) {
  const zh = locale === "zh";
  return (
    <main className="text-page">
      <span className="eyebrow">MODEL REVIEW</span>
      <h1>{zh ? "赛后复盘" : "Post-match review"}</h1>
      <p className="lead">{zh ? "赛前预测永久保留，并与实际结果对比，持续识别模型偏差。" : "Pre-match forecasts remain unchanged and are compared with actual results to identify model bias."}</p>
      <div className="review-list">
        {matches.map((match) => (
          <article className="review-card" key={match.id}>
            <div className="review-heading"><div><span>{zh ? match.stageZh : match.stage}</span><h2>{localTeam(match.homeTeam, locale)} vs {localTeam(match.awayTeam, locale)}</h2><small>{formatKickoff(match.kickoff, locale).utc}</small></div><div className="review-scores"><div><small>{zh ? "预测比分" : "Predicted"}</small><b>{match.likelyScore}</b></div><i>→</i><div><small>{zh ? "实际比分" : "Actual"}</small><b>{match.actualScore}</b></div></div></div>
            <p className="result-note">{zh ? match.resultNoteZh : match.resultNote}</p>
            <div className="review-probabilities"><span>{localTeam(match.homeTeam, locale)} {match.homeWin}%</span><span>{zh ? "平局" : "Draw"} {match.draw}%</span><span>{localTeam(match.awayTeam, locale)} {match.awayWin}%</span></div>
            <div className="error-analysis"><strong>{zh ? "可能的失误原因" : "Possible error drivers"}</strong><ul>{(zh ? match.errorReasonsZh : match.errorReasons)?.map((reason) => <li key={reason}>{reason}</li>)}</ul></div>
          </article>
        ))}
      </div>
    </main>
  );
}
