"use client";
import { FormEvent, useState } from "react";
import { api } from "../../lib/api";

type Result = { character_count: number; word_count: number; unique_word_count: number; frequent_words: { word: string; count: number }[] };
const example = "Learning Python opens doors. Learning by building makes Python stick.";

export default function Analyzer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setResult(null); setBusy(true);
    try { setResult(await api<Result>("/analysis", { method: "POST", body: JSON.stringify({ text }) })); }
    catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }
  return <>
    <p className="text-sm font-semibold uppercase tracking-widest text-teal-800">01 / Text & data</p>
    <h1 className="mt-3 text-4xl font-bold tracking-tight">A closer look at your words.</h1>
    <p className="mt-4 max-w-2xl text-slate-600">Paste a paragraph and discover its vocabulary. Your text is analyzed on submission and is not saved.</p>
    <div className="mt-8 grid items-start gap-6 lg:grid-cols-2">
      <form onSubmit={submit} className="panel">
        <label htmlFor="text" className="font-semibold">Your text</label>
        <textarea id="text" className="field mt-3 min-h-64 resize-y" value={text} onChange={e => { setText(e.target.value); setResult(null); }} maxLength={50000} required disabled={busy} aria-describedby="text-help"/>
        <p id="text-help" className="mt-2 text-sm text-slate-500">{text.length.toLocaleString()} / 50,000 characters · punctuation separates words; apostrophes inside words stay.</p>
        <div className="mt-6 flex flex-wrap gap-3"><button className="button" disabled={busy || !text.trim()}>{busy ? "Analyzing…" : "Analyze text"}</button><button type="button" className="secondary" disabled={busy} onClick={() => { setText(example); setResult(null); setError(""); }}>Try an example</button></div>
        {error && <p role="alert" className="mt-5 text-sm text-red-800">{error}</p>}
      </form>
      <section className="panel" aria-label="Analysis results" aria-live="polite" aria-busy={busy}>
        <h2 className="text-xl font-bold">Your results</h2>
        {!result ? <p className="mt-5 py-12 text-slate-500">{busy ? "Looking for the patterns in your text…" : "Add some text and select Analyze text to see the results here."}</p> : <>
          <dl className="mt-6 grid grid-cols-3 gap-3">{[["Characters", result.character_count], ["Words", result.word_count], ["Unique words", result.unique_word_count]].map(([label, value]) => <div key={label} className="rounded-xl bg-teal-50 p-3"><dt className="text-xs text-teal-900">{label}</dt><dd className="mt-2 text-2xl font-bold">{value.toLocaleString()}</dd></div>)}</dl>
          <h3 className="mt-8 font-semibold">Most frequent words</h3>
          {result.frequent_words.length ? <table className="mt-3 w-full text-left text-sm"><caption className="sr-only">The ten most frequent words, with counts</caption><thead><tr className="border-b border-slate-200"><th className="py-3">Word</th><th className="py-3 text-right">Count</th></tr></thead><tbody>{result.frequent_words.map(w => <tr key={w.word} className="border-b border-slate-100"><td className="py-3">{w.word}</td><td className="text-right">{w.count}</td></tr>)}</tbody></table> : <p className="mt-3 text-slate-500">No words found in this text.</p>}
          <p className="mt-5 text-xs leading-relaxed text-slate-500">Counts ignore case for words. Character count includes spaces and punctuation and uses Python Unicode code points. Frequency ties are sorted alphabetically.</p>
        </>}
      </section>
    </div>
  </>;
}
