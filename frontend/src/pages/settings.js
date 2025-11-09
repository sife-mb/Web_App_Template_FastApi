// src/pages/settings.js
import Layout from "../components/Layout";

export default function SettingsPage() {
  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">Benutzereinstellungen</h2>
        <p className="mb-4">Hier kannst du später deine Dashboard-Einstellungen ändern.</p>

        {/* Dummy Inputs */}
        <label className="block mb-2">
          <span className="text-gray-700">Theme:</span>
          <select className="mt-1 block w-full rounded border-gray-300">
            <option>Light</option>
            <option>Dark</option>
          </select>
        </label>

        <label className="block mb-2">
          <span className="text-gray-700">Sprache:</span>
          <select className="mt-1 block w-full rounded border-gray-300">
            <option>Deutsch</option>
            <option>Englisch</option>
          </select>
        </label>
      </div>
    </Layout>
  );
}