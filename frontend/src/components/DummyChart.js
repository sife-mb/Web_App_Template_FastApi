import dynamic from "next/dynamic";
import { useEffect, useState } from "react";


// Dynamischer Import von Plotly (SSR deaktiviert - nur clientseitig gerendert)
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// DummyChart-Komponente
const DummyChart = ({ title = "Dummy Time Series" }) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Dummy-Zeitreihe generieren
    const x = Array.from({ length: 100 }, (_, i) => i);
    const y = Array.from({ length: 100 }, () => Math.random() * 10);
    setData([{ x, y, type: "scatter", mode: "lines+markers", marker: { color: "blue" } }]);
  }, []);



  return (
    <Plot
      data={data}
      layout={{ title, autosize: true }}
      useResizeHandler
      style={{ width: "100%", height: "100%" }}
    />
  );
};

export default DummyChart;