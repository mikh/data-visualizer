import { useState, useEffect } from "react";

const URL_PREFIX = import.meta.env.VITE_URL_PREFIX || "http://127.0.0.1:5000";
const REACT_VERSION = import.meta.env.VITE_REACT_VERSION || "0.0.0";

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
    <header className="bg-slate-800 text-white px-8 py-4 flex justify-between items-center shadow">
      <h1 className="m-0 text-2xl font-bold">Data Visualization</h1>
      <div>
        <div className="text-sm opacity-80">
          {loading ? "Loading version..." : error ? error : `Flask v${version}`}
        </div>
        <div className="text-sm opacity-80">React v{REACT_VERSION}</div>
      </div>
    </header>
  );
}
