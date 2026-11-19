import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DecisionFlow | AI Decision Flow with React Flow + Inngest",
  description: "Visual AI workflow engine with Inngest step orchestration and binary YES/NO branching.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased overflow-hidden">
        {children}
      </body>
    </html>
  );
}
