// components/Layout.js
import { useSession } from "next-auth/react";
import Link from "next/link"; 
import Sidebar from "./Sidebar";

export default function Layout({ children }) {
  const { data: session } = useSession();
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
