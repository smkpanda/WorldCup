import { Pool } from "pg";
import { demoPredictions } from "./demo-data";
import type { Prediction } from "./types";

let pool: Pool | undefined;

function getPool() {
  if (!process.env.DATABASE_URL) return undefined;
  pool ??= new Pool({ connectionString: process.env.DATABASE_URL, max: 3 });
  return pool;
}

export async function getPredictions(): Promise<Prediction[]> {
  const db = getPool();
  if (!db) return demoPredictions;

  try {
    const result = await db.query<{ payload: Prediction }>(
      `select payload from predictions
       where published = true
       order by (payload->>'kickoff')::timestamptz asc`,
    );
    return result.rows.length ? result.rows.map((row) => row.payload) : demoPredictions;
  } catch (error) {
    console.error("Database unavailable; using demo predictions", error);
    return demoPredictions;
  }
}

export async function getPrediction(id: string): Promise<Prediction | undefined> {
  return (await getPredictions()).find((prediction) => prediction.id === id);
}
