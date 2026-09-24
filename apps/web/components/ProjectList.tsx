import Link from "next/link";
import { Project } from "../lib/api";

export default function ProjectList({ projects }: { projects: Project[] }) {
  return (
    <section className="card">
      <div className="section-head">
        <div>
          <p className="eyebrow">PROJECTS</p>
          <h2>Recent videos</h2>
        </div>
        <span className="pill">{projects.length}</span>
      </div>
      {projects.length === 0 ? <p className="muted">No projects yet.</p> : (
        <div className="project-list">
          {projects.map((project) => (
            <Link className="project-row" href={`/project/${project.id}`} key={project.id}>
              <div><strong>{project.name}</strong><span>{project.source_filename}</span></div>
              <span className={`status ${project.status}`}>{project.status}</span>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
