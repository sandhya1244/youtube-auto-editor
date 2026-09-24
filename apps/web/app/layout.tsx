import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "YouTube Auto Editor",
  description: "Automated video editing for YouTube creators"
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
