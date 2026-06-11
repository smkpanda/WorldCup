export type Team = {
  id: string;
  code: string;
  name: string;
  nameZh: string;
  flag: string;
  fifaRank: number;
  squadValueM: number;
  form: string[];
};

export type ScoreProbability = {
  home: number;
  away: number;
  probability: number;
};

export type PlayerImpact = {
  name: string;
  position: string;
  positionZh: string;
  teamCode: string;
  goals: number;
  assists: number;
  minutes: number;
  rating: number;
};

export type Prediction = {
  id: string;
  kickoff: string;
  stage: string;
  stageZh: string;
  venue: string;
  venueZh: string;
  status: "upcoming" | "finished";
  homeTeam: Team;
  awayTeam: Team;
  homeWin: number;
  draw: number;
  awayWin: number;
  expectedHomeGoals: number;
  expectedAwayGoals: number;
  likelyScore: string;
  topScores: ScoreProbability[];
  confidence: number;
  factors: { label: string; labelZh: string; home: number; away: number; note: string; noteZh: string }[];
  keyPlayers: PlayerImpact[];
  modelVersion: string;
  dataVersion: string;
  updatedAt: string;
  actualScore?: string;
  resultNote?: string;
  resultNoteZh?: string;
  errorReasons?: string[];
  errorReasonsZh?: string[];
};
