import { notFound } from "next/navigation";
import HomePage from "@/components/home-page";
import { getPredictions } from "@/lib/data";
import { isLocale } from "@/lib/i18n";

export default async function LocalizedHome({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  return <HomePage predictions={await getPredictions()} locale={locale} />;
}
