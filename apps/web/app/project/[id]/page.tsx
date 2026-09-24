import Link from "next/link";
import EditorPanel from "../../../components/EditorPanel";
import { getProject } from "../../../lib/api";

export const dynamic = "force-dynamic";

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const project = await getProject(id);
  return (
    <main className="page-shell">
      <header className="topbar"><Link href="/" className="ghost-link">← Projects</Link><span className="pill">{project.status}</span></header>
      <EditorPanel project={project} />
    </main>
  );
}
