import { useState, useEffect } from "react";

const URL_PREFIX = import.meta.env.VITE_URL_PREFIX || "http://127.0.0.1:5000";

export default function Header() {
  const [version, setVersion] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const response = await fetch(`${URL_PREFIX}/api/version`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setVersion(data.version);
      } catch (err) {
        setError("Failed to fetch version");
        console.error("Error fetching version:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchVersion();
  }, []);

  return (
    <header
      style={{
        backgroundColor: "#2c3e50",
        color: "white",
        padding: "1rem 2rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
      }}
    >
      <h1 style={{ margin: 0, fontSize: "1.8rem", fontWeight: "bold" }}>
        Data Visualization
      </h1>
      <div style={{ fontSize: "0.9rem", opacity: 0.8 }}>
        {loading ? "Loading version..." : error ? error : `v${version}`}
      </div>
    </header>
  );
}
