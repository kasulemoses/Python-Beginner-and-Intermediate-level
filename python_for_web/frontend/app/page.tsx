import Link from "next/link";

export default function Home() {
  return <>
    <p className="mb-5 text-sm font-semibold uppercase tracking-widest text-teal-800">30 days of Python / the web chapters</p>
    <h1 className="max-w-3xl text-4xl font-bold leading-tight tracking-tight sm:text-6xl">Put your Python<br/>into practice.</h1>
    <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-600">Explore the patterns in your words. Build a directory of learners. Connect the Python you know to an interface you can use.</p>
    <div className="mt-10 grid gap-6 md:grid-cols-2">
      <Link href="/analyzer" className="panel block transition hover:border-teal-600"><p className="text-sm font-semibold text-teal-800">01 / TEXT & DATA</p><h2 className="mt-5 text-2xl font-bold">See what your words say</h2><p className="mt-3 leading-relaxed text-slate-600">Count characters, explore vocabulary, and find the words you use most.</p><span className="mt-8 inline-block font-semibold text-teal-800">Open text analyzer →</span></Link>
      <Link href="/students" className="panel block transition hover:border-teal-600"><p className="text-sm font-semibold text-teal-800">02 / THE STUDENT DIRECTORY</p><h2 className="mt-5 text-2xl font-bold">Make a little room to learn</h2><p className="mt-3 leading-relaxed text-slate-600">Create fictional learner profiles and practice managing real, persistent records.</p><span className="mt-8 inline-block font-semibold text-teal-800">Explore students →</span></Link>
    </div>
  </>;
}
