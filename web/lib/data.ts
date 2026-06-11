import predictions from "@/data/predictions.json";
import type { Prediction } from "./types";

const data = predictions as Prediction[];

export async function getPredictions(): Promise<Prediction[]> {
  return data;
}

export async function getPrediction(id: string): Promise<Prediction | undefined> {
  return data.find((prediction) => prediction.id === id);
}
