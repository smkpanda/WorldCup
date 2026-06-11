import { notFound } from "next/navigation";
import ReviewPageView from "@/components/review-page";
import { getPredictions } from "@/lib/data";
import { isLocale } from "@/lib/i18n";

export default async function LocalizedReview({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const matches = (await getPredictions()).filter((match) => match.status === "finished");
  return <ReviewPageView matches={matches} locale={locale} />;
}
