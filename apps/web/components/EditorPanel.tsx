"use client";

import { useEffect, useState } from "react";
import { API_BASE, Project, mediaUrl } from "../lib/api";

export default function EditorPanel({ project }: { project: Project }) {
  const [removeSilence, setRemoveSilence] = useState(true);
  const [removeFillers, setRemoveFillers] = useState(false);
  const [captions, setCaptions] = useState(true);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string>("");
  const [youtubeUrl, setYoutubeUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) return;
    const timer = setInterval(async () => {
      const res = await fetch(`${API_BASE}/api/jobs/${taskId}`, { cache: "no-store" });
      const job = await res.json();
      setJobStatus(job.status);
      if (["success", "failure", "revoked"].includes(job.status)) clearInterval(timer);
      if (job.status === "success") window.location.reload();
    }, 1500);
    return () => clearInterval(timer);
  }, [taskId]);

  async function render() {
    const res = await fetch(`${API_BASE}/api/projects/${project.id}/render`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ remove_silence: removeSilence, remove_filler_words: removeFillers, generate_captions: captions })
    });
    const job = await res.json();
    setTaskId(job.task_id);
    setJobStatus(job.status);
  }

  async function connectYoutube() {
    const res = await fetch(`${API_BASE}/api/youtube/auth`);
    const data = await res.json();
    window.location.href = data.url;
  }

  async function uploadYoutube() {
    const title = window.prompt("YouTube title", project.name) ?? project.name;
    const description = window.prompt("YouTube description", "Edited with YouTube Auto Editor") ?? "";
    const res = await fetch(`${API_BASE}/api/youtube/projects/${project.id}/upload`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description, tags: [], privacy_status: "private" })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail ?? "YouTube upload failed");
    setYoutubeUrl(data.url);
  }

  const videoSrc = project.rendered_path ? mediaUrl(project.rendered_path) : mediaUrl(project.source_path);

  return (
    <div className="editor-grid">
      <section className="card video-card">
        <p className="eyebrow">PREVIEW</p>
        <h2>{project.name}</h2>
        <video controls className="video" src={videoSrc} />
        <div className="timeline"><span>0:00</span><div className="timeline-track"><i /></div><span>{project.duration_seconds ? `${Math.floor(project.duration_seconds / 60)}:${String(Math.floor(project.duration_seconds % 60)).padStart(2, "0")}` : "—"}</span></div>
      </section>
      <aside className="card controls">
        <p className="eyebrow">AUTOMATION</p>
        <h2>AI edit recipe</h2>
        <label className="check"><input type="checkbox" checked={removeSilence} onChange={(e) => setRemoveSilence(e.target.checked)} /> Remove silence</label>
        <label className="check"><input type="checkbox" checked={removeFillers} onChange={(e) => setRemoveFillers(e.target.checked)} /> Remove filler words</label>
        <label className="check"><input type="checkbox" checked={captions} onChange={(e) => setCaptions(e.target.checked)} /> Generate captions</label>
        <button className="button" onClick={render} disabled={jobStatus === "started" || jobStatus === "pending"}>Render video</button>
        {jobStatus && <p className="muted">Render job: <strong>{jobStatus}</strong></p>}
        {project.rendered_path && <a className="button secondary" href={videoSrc} target="_blank" rel="noreferrer">Open rendered video</a>}
        <hr />
        <h3>YouTube</h3>
        <button className="button secondary" onClick={connectYoutube}>Connect YouTube</button>
        <button className="button secondary" disabled={!project.rendered_path} onClick={() => uploadYoutube().catch((e) => alert(e.message))}>Upload as private</button>
        {youtubeUrl && <a href={youtubeUrl} target="_blank" rel="noreferrer">View on YouTube</a>}
        <p className="tiny">Uploads are private by default in this starter.</p>
      </aside>
    </div>
  );
}
