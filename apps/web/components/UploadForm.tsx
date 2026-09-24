"use client";

import { useState } from "react";
import { API_BASE } from "../lib/api";

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    if (!file) return;
    setBusy(true);
    setError("");
    const form = new FormData();
    form.append("file", file);
    if (name.trim()) form.append("name", name.trim());
    try {
      const res = await fetch(`${API_BASE}/api/projects`, { method: "POST", body: form });
      if (!res.ok) throw new Error((await res.json()).detail ?? "Upload failed");
      const project = await res.json();
      window.location.href = `/project/${project.id}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card upload-card">
      <div>
        <p className="eyebrow">NEW PROJECT</p>
        <h2>Drop in a YouTube video</h2>
        <p className="muted">Start with MP4, MOV, MKV, or WebM. The worker handles the heavy video processing.</p>
      </div>
      <label className="dropzone">
        <input type="file" accept="video/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <strong>{file ? file.name : "Choose a video"}</strong>
        <span>{file ? `${(file.size / 1024 / 1024).toFixed(1)} MB` : "or drag and drop it here"}</span>
      </label>
      <input className="text-input" placeholder="Project name (optional)" value={name} onChange={(e) => setName(e.target.value)} />
      {error && <p className="error">{error}</p>}
      <button className="button" disabled={!file || busy} onClick={submit}>{busy ? "Uploading…" : "Create project"}</button>
    </section>
  );
}
