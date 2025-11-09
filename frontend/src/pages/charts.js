// src/pages/charts.js
import Layout from "../components/Layout";
import DummyChart from "../components/DummyChart";

export default function ChartsPage() {
  const grafanaEmbedUrl = "http://localhost:3000/d-solo/ad9zlw2/new-dashboard?orgId=1&panelId=2&from=now-15m&to=now";
  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-4">Charts</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        
        {/* --- HIER IST DEIN GRAFANA-PANEL --- */}
        {/* Ich habe den DummyChart durch das iframe ersetzt */}
        {/* Ich habe dem Panel eine Höhe (h-80) gegeben, damit das iframe Platz hat */}
        <div className="panel bg-gray-800 p-4 rounded-md h-80"> 
          <iframe
            src={grafanaEmbedUrl} // Nutzt die Variable von oben
            width="100%"
            height="100%"
            frameBorder="0"
            className="rounded-md"
          ></iframe>
        </div>
        <div className="panel bg-gray-100 p-4">
          <DummyChart title="Visitors" />
        </div>
        <div className="panel bg-gray-100 p-4">
          <DummyChart title="Revenue" />
        </div>
        <div className="panel bg-gray-100 p-4">
          <DummyChart title="Anomalies" />
        </div>
      </div>
    </Layout>
  );
}