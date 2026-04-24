import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bandit Beats — RL Music Recommender",
  description:
    "Context-aware music recommendations powered by multi-armed bandit reinforcement learning.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-animated">{children}</body>
    </html>
  );
}
