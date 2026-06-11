create table if not exists teams (
  id uuid primary key,
  code text not null unique,
  name text not null,
  payload jsonb not null default '{}'
);

create table if not exists players (
  id uuid primary key,
  team_id uuid references teams(id),
  source_player_id text not null,
  name text not null,
  position text not null,
  payload jsonb not null default '{}',
  unique (source_player_id, team_id)
);

create table if not exists matches (
  id text primary key,
  competition text not null,
  kickoff timestamptz not null,
  home_team_id uuid references teams(id),
  away_team_id uuid references teams(id),
  status text not null,
  payload jsonb not null default '{}'
);

create table if not exists squad_snapshots (
  id bigserial primary key,
  team_id uuid references teams(id),
  match_id text references matches(id),
  captured_at timestamptz not null,
  is_confirmed boolean not null default false,
  payload jsonb not null
);

create table if not exists player_match_stats (
  id bigserial primary key,
  player_id uuid references players(id),
  competition text not null,
  occurred_at timestamptz not null,
  minutes integer not null check (minutes between 0 and 600),
  source text not null,
  payload jsonb not null
);

create table if not exists valuation_snapshots (
  id bigserial primary key,
  player_id uuid references players(id),
  value_eur numeric not null check (value_eur >= 0),
  captured_at timestamptz not null,
  source text not null
);

create table if not exists ranking_snapshots (
  id bigserial primary key,
  team_id uuid references teams(id),
  ranking_type text not null,
  rank integer not null,
  points numeric,
  captured_at timestamptz not null
);

create table if not exists predictions (
  id text primary key,
  match_id text not null,
  model_version text not null,
  data_version text not null,
  payload jsonb not null,
  published boolean not null default false,
  published_at timestamptz,
  unique (match_id, model_version, data_version)
);

create index if not exists predictions_published_idx on predictions (published, published_at desc);

create table if not exists data_runs (
  id bigserial primary key,
  source text not null,
  status text not null,
  details jsonb not null default '{}',
  started_at timestamptz not null default now(),
  finished_at timestamptz
);
