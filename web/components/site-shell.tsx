"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { copy, type Locale } from "@/lib/i18n";

function localeFromPath(pathname: string): Locale {
  return pathname.startsWith("/zh") ? "zh" : "en";
}

export default function SiteShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const locale = localeFromPath(pathname);
  const text = copy[locale];
  const alternate = locale === "en" ? "zh" : "en";
  const alternatePath = pathname.replace(/^\/(en|zh)/, `/${alternate}`) || `/${alternate}`;

  return (
    <>
      <header className="site-header">
        <Link href={`/${locale}`} className="brand">
          <span className="brand-mark">W</span>
          <span>{text.brand}</span>
        </Link>
        <nav>
          <Link href={`/${locale}`}>{text.predictions}</Link>
          <Link href={`/${locale}/review`}>{text.review}</Link>
          <Link href={`/${locale}/methodology`}>{text.methodology}</Link>
        </nav>
        <div className="header-actions">
          <Link className="language-switch" href={alternatePath}>{locale === "en" ? "中文" : "EN"}</Link>
          <div className="live-pill"><i /> {text.online}</div>
        </div>
      </header>
      {children}
      <footer>
        <div><strong>{text.brand}</strong><p>{text.tagline}</p></div>
        <p>{text.disclaimer}</p>
      </footer>
    </>
  );
}
