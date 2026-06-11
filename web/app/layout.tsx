import type { Metadata } from "next";
import SiteShell from "@/components/site-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "Match Forecast | 2026 World Cup",
  description: "An explainable, data-informed entertainment forecast for the 2026 World Cup.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <SiteShell>{children}</SiteShell>
      </body>
    </html>
  );
}
