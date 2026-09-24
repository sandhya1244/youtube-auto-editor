import UploadForm from "../components/UploadForm";
import ProjectList from "../components/ProjectList";
import { getProjects } from "../lib/api";

export const dynamic = "force-dynamic";

export default async function Home() {
  const projects = await getProjects().catch(() => []);
  return (
    <main className="page-shell">
      <header className="topbar"><div><div className="brand">AUTO CUT <span>YT</span></div><p className="muted">Automated editing workspace</p></div><a className="ghost-link" href="http://localhost:8000/docs" target="_blank" rel="noreferrer">API docs ↗</a></header>
      <section className="hero"><div><p className="eyebrow">YOUTUBE VIDEO EDITOR</p><h1>Turn raw footage into a publish-ready cut.</h1><p className="hero-copy">Upload a video, choose an automation recipe, render with FFmpeg, then send the result to YouTube.</p></div></section>
      <div className="stack"><UploadForm /><ProjectList projects={projects} /></div>
    </main>
  );
}
