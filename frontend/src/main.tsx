import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  const [status, setStatus] = useState("Connecting to the application service…");

  useEffect(() => {
    fetch("/bff/v1/bootstrap")
      .then((response) => {
        if (!response.ok) throw new Error("BFF unavailable");
        return response.json();
      })
      .then((payload: { application: { name: string } }) => setStatus(`${payload.application.name} connected`))
      .catch(() => setStatus("Application service temporarily unavailable"));
  }, []);

  return (
    <main>
      <p className="eyebrow">RAG PARSE</p>
      <h1>Trusted Document Q&amp;A Platform</h1>
      <p>{status}</p>
      <p>Sign-in, knowledge bases, and traceable retrieval will be added here.</p>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
