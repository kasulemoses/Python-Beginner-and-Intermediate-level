import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Python Learning Lab", template: "%s | Python Learning Lab" },
  description: "Explore text analysis and a student directory built with Python.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>
    <a href="#main" className="sr-only focus:not-sr-only focus:block focus:p-4">Skip to content</a>
    <header className="border-b border-slate-200 bg-white">
      <nav aria-label="Main navigation" className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-5 px-6 py-5">
        <Link href="/" className="text-lg font-bold tracking-tight">Python<span className="text-teal-700"> / learning lab</span></Link>
        <div className="flex gap-5 text-sm font-medium"><Link href="/analyzer">Text analyzer</Link><Link href="/students">Students</Link><Link href="/about">About</Link></div>
      </nav>
    </header>
    <main id="main" className="mx-auto max-w-6xl px-6 py-10 sm:py-16">{children}</main>
    <footer className="mx-auto max-w-6xl border-t border-slate-200 px-6 py-8 text-sm text-slate-600">30 Days of Python · Learn by building, one working feature at a time.</footer>
  </body></html>;
}
