import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Badminton Dataset Generator",
  description: "Collect and curate badminton footage frames for CVAT annotation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <body className="min-h-screen bg-background font-sans antialiased">
        <TooltipProvider>
          <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
              <a href="/" className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-bold text-sm">
                  BD
                </div>
                <div>
                  <h1 className="text-base font-semibold tracking-tight text-foreground">
                    Badminton Dataset Generator
                  </h1>
                  <p className="text-xs text-muted-foreground">CVAT Image Collection Pipeline</p>
                </div>
              </a>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </TooltipProvider>
      </body>
    </html>
  );
}
