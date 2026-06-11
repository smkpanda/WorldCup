import { notFound } from "next/navigation";
import MatchDetail from "@/components/match-detail";
import { getPrediction } from "@/lib/data";
import { isLocale } from "@/lib/i18n";

export default async function LocalizedMatch({ params }: { params: Promise<{ locale: string; id: string }> }) {
  const { locale, id } = await params;
  if (!isLocale(locale)) notFound();
  const match = await getPrediction(id);
  if (!match) notFound();
  return <MatchDetail match={match} locale={locale} />;
}
