export function probabilityTotal(home: number, draw: number, away: number) {
  return Math.round((home + draw + away) * 100) / 100;
}

export function formatPercent(value: number) {
  return `${Math.round(value)}%`;
}
