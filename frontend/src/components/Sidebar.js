import Link from "next/link";
import { useSession } from "next-auth/react"; // 1. HIER IMPORTIEREN

export default function Sidebar() {
  // 2. HIER DIE SESSION HOLEN
  const { data: session } = useSession();

  return (
    <div className="h-screen w-64 bg-gray-800 text-white flex flex-col p-4">
      <h2 className="text-xl font-bold mb-6">Mein Dashboard</h2>
      <nav className="flex flex-col gap-4">
        <Link href="/" className="hover:text-gray-300">🏠 Home</Link>
        
        {/* 3. HIER DIE ÄNDERUNG FÜR DEN CHARTS-LINK */}
        {session ? (
          // Eingeloggt: Normaler Link
          <Link href="/charts" className="hover:text-gray-300">
            📊 Charts
          </Link>
        ) : (
          // Ausgeloggt: Ausgegrauter, nicht klickbarer Text
          <span className="text-gray-500 cursor-not-allowed">
            📊 Charts
          </span>
        )}

        <Link href="/settings" className="hover:text-gray-300">⚙️ Settings</Link>
      </nav>
    </div>
  );
}