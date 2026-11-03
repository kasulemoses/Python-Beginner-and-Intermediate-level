"use client";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { api } from "../../lib/api";

type Student = { id: string; name: string; country: string; city: string; date_of_birth: string; skills: string[]; bio: string; created_at: string; updated_at: string };
type Page = { items: Student[]; total: number; offset: number; limit: number };
type Draft = { name: string; country: string; city: string; date_of_birth: string; skills: string; bio: string };
const blank: Draft = { name: "", country: "", city: "", date_of_birth: "", skills: "", bio: "" };
const limit = 10;

export default function Students() {
  const [page, setPage] = useState<Page | null>(null);
  const [offset, setOffset] = useState(0);
  const [filter, setFilter] = useState("");
  const [country, setCountry] = useState("");
  const [version, setVersion] = useState(0);
  const [draft, setDraft] = useState<Draft>(blank);
  const [selected, setSelected] = useState<Student | null>(null);
  const [editing, setEditing] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const form = useRef<HTMLFormElement>(null);
  const sequence = useRef(0);
  const load = useCallback(async () => {
    const current = ++sequence.current;
    setLoading(true); setError("");
    try {
      const query = new URLSearchParams({ offset: String(offset), limit: String(limit) });
      if (country) query.set("country", country);
      const result = await api<Page>("/students?" + query);
      if (current === sequence.current) {
        if (offset > 0 && result.items.length === 0) setOffset(Math.max(0, offset - limit));
        else setPage(result);
      }
    } catch (e) { if (current === sequence.current) { setError((e as Error).message); setPage(null); } }
    finally { if (current === sequence.current) setLoading(false); }
  }, [country, offset]);
  useEffect(() => { void load(); return () => { sequence.current++; }; }, [load, version]);
  async function save(event: FormEvent) {
    event.preventDefault(); setSaving(true); setError(""); setNotice("");
    const payload = { ...draft, skills: draft.skills.split(",").map(s => s.trim()).filter(Boolean) };
    try {
      const student = await api<Student>(editing ? "/students/" + editing : "/students", {
        method: editing ? "PATCH" : "POST", body: JSON.stringify(payload),
      });
      setNotice(editing ? "Student updated." : "Student created.");
      setSelected(student); setDraft(blank); setEditing(null); setVersion(v => v + 1);
    } catch (e) { setError((e as Error).message); }
    finally { setSaving(false); }
  }
  async function details(id: string) {
    setSaving(true); setError("");
    try { setSelected(await api<Student>("/students/" + id)); }
    catch (e) { setError((e as Error).message); }
    finally { setSaving(false); }
  }
  function edit(student: Student) {
    setEditing(student.id); setDraft({ name: student.name, country: student.country, city: student.city, date_of_birth: student.date_of_birth, skills: student.skills.join(", "), bio: student.bio });
    form.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    form.current?.querySelector<HTMLInputElement>("input")?.focus();
  }
  async function remove(student: Student) {
    if (!window.confirm("Delete " + student.name + "? This cannot be undone.")) return;
    setSaving(true); setError(""); setNotice("");
    try {
      await api<void>("/students/" + student.id, { method: "DELETE" });
      if (selected?.id === student.id) setSelected(null);
      if (editing === student.id) { setEditing(null); setDraft(blank); }
      setNotice("Student deleted."); setVersion(v => v + 1);
    } catch (e) { setError((e as Error).message); }
    finally { setSaving(false); }
  }
  return <>
    <p className="text-sm font-semibold uppercase tracking-widest text-teal-800">02 / The student directory</p>
    <h1 className="mt-3 text-4xl font-bold tracking-tight">A place for every learner.</h1>
    <p className="mt-4 max-w-2xl text-slate-600">Practice with fictional profiles. Add a learner, explore their skills, and keep their details up to date.</p>
    {error && <div role="alert" className="mt-6 rounded-xl bg-red-50 p-4 text-red-900">{error} <button className="ml-2 underline" disabled={loading || saving} onClick={() => setVersion(v => v + 1)}>Retry loading directory</button></div>}
    <p role="status" className="mt-4 text-sm text-teal-800">{notice}</p>
    <div className="mt-5 grid items-start gap-6 lg:grid-cols-[1.5fr_1fr]">
      <section className="panel" aria-label="Student directory" aria-busy={loading}>
        <div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-bold">Directory</h2><span className="text-sm text-slate-500">{page && !loading ? page.total + " learners" : ""}</span></div>
        <form className="mt-5 flex flex-wrap items-end gap-2" onSubmit={e => { e.preventDefault(); setOffset(0); setCountry(filter.trim()); }}>
          <div className="min-w-0 flex-1"><label htmlFor="country-filter" className="text-sm font-medium">Filter by country (exact match)</label><input id="country-filter" className="field mt-2" value={filter} onChange={e => setFilter(e.target.value)} maxLength={100}/></div>
          <button className="secondary" disabled={saving || loading}>Apply</button>
          {country && <button type="button" className="secondary" disabled={saving || loading} onClick={() => { setCountry(""); setFilter(""); setOffset(0); }}>Clear</button>}
        </form>
        {loading ? <p role="status" className="py-12 text-slate-500">Loading students…</p> : page ? <>
          {page.items.length === 0 ? <p className="py-12 text-slate-500">{country ? "No learners match this country." : "The directory is empty. Add your first fictional learner."}</p> :
            <ul className="mt-6 divide-y divide-slate-200">{page.items.map(student => <li key={student.id} className="py-5">
              <button onClick={() => void details(student.id)} disabled={saving} className="text-left text-lg font-semibold text-teal-800 underline decoration-teal-200 underline-offset-4">{student.name}</button>
              <p className="mt-1 text-sm text-slate-500">{student.city}, {student.country}</p><p className="mt-2 text-sm">{student.skills.join(" · ") || "No skills added yet"}</p>
              <div className="mt-3 flex gap-3"><button className="secondary" disabled={saving} onClick={() => edit(student)}>Edit <span className="sr-only">{student.name}</span></button><button className="secondary text-red-800" disabled={saving} onClick={() => void remove(student)}>Delete <span className="sr-only">{student.name}</span></button></div>
            </li>)}</ul>}
          <div className="mt-5 flex items-center justify-between gap-2 border-t border-slate-200 pt-5"><button className="secondary" disabled={offset === 0 || saving} onClick={() => setOffset(o => Math.max(0, o - limit))}>Previous</button><span className="text-xs text-slate-500">{page.total ? offset + 1 : 0}–{Math.min(offset + limit, page.total)} of {page.total}</span><button className="secondary" disabled={offset + limit >= page.total || saving} onClick={() => setOffset(o => o + limit)}>Next</button></div>
        </> : <p className="py-8 text-slate-500">The directory could not be loaded. Your form entries are preserved.</p>}
      </section>
      <div className="space-y-6">
        <form ref={form} onSubmit={save} className="panel">
          <h2 className="text-xl font-bold">{editing ? "Edit learner" : "Add a learner"}</h2>
          <fieldset disabled={saving}><legend className="sr-only">Learner details</legend>
            {(["name", "country", "city", "date_of_birth", "skills"] as const).map(key => <div key={key} className="mt-4">
              <label htmlFor={key} className="text-sm font-medium">{({ name: "Name", country: "Country", city: "City", date_of_birth: "Date of birth", skills: "Skills (comma separated)" })[key]}{key !== "skills" && " *"}</label>
              <input id={key} type={key === "date_of_birth" ? "date" : "text"} className="field mt-2" value={draft[key]} required={key !== "skills"} maxLength={key === "skills" ? 1800 : 100} max={key === "date_of_birth" ? new Date().toISOString().slice(0, 10) : undefined} onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))}/>
            </div>)}
            <label htmlFor="bio" className="mt-4 block text-sm font-medium">Bio</label><textarea id="bio" className="field mt-2" rows={3} maxLength={2000} value={draft.bio} onChange={e => setDraft(d => ({ ...d, bio: e.target.value }))}/>
            <div className="mt-5 flex gap-3"><button className="button">{saving ? "Working…" : editing ? "Save changes" : "Create student"}</button>{editing && <button type="button" className="secondary" onClick={() => { setEditing(null); setDraft(blank); }}>Cancel</button>}</div>
          </fieldset>
        </form>
        {selected && <section className="panel" aria-label="Selected student"><h2 className="text-xl font-bold">{selected.name}</h2><dl className="mt-4 space-y-3 text-sm"><div><dt className="text-slate-500">Location</dt><dd>{selected.city}, {selected.country}</dd></div><div><dt className="text-slate-500">Date of birth</dt><dd>{selected.date_of_birth}</dd></div><div><dt className="text-slate-500">Skills</dt><dd>{selected.skills.join(", ") || "None yet"}</dd></div><div><dt className="text-slate-500">Bio</dt><dd className="whitespace-pre-wrap break-words">{selected.bio || "No bio yet"}</dd></div></dl><button className="secondary mt-5" disabled={saving} onClick={() => edit(selected)}>Edit profile</button></section>}
      </div>
    </div>
  </>;
}
