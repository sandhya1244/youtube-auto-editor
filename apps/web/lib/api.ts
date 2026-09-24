export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Project = {
  source_path: string;
  id: number;
  name: string;
  source_filename: string;
  rendered_path: string | null;
  status: string;
  duration_seconds: number | null;
  captions_enabled: boolean;
  created_at: string;
  updated_at: string;
};

export async function getProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/api/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load projects");
  return res.json();
}

export async function getProject(id: string): Promise<Project> {
  const res = await fetch(`${API_BASE}/api/projects/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Project not found");
  return res.json();
}

export function mediaUrl(relativePath: string) {
  const marker = "/app/data/";
  const index = relativePath.indexOf(marker);
  const relative = index >= 0 ? relativePath.slice(index + marker.length) : relativePath;
  return `${API_BASE}/media/${relative}`;
}
