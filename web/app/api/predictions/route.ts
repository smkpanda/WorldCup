import { getPredictions } from "@/lib/data";

export async function GET() {
  return Response.json({
    data: await getPredictions(),
    disclaimer: "娱乐预测，不构成任何投注或投资建议。",
  });
}
