// src/pages/charts.js
import Layout from "../components/Layout";
import DummyChart from "../components/DummyChart";

export default function ChartsPage() {
  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-4">Charts</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="panel bg-gray-100 p-4">
          <DummyChart title="Sales over Time" />
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