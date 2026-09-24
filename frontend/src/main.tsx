import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  const [status, setStatus] = useState("正在连接应用服务…");

  useEffect(() => {
    fetch("/bff/v1/bootstrap")
      .then((response) => {
        if (!response.ok) throw new Error("BFF unavailable");
        return response.json();
      })
      .then((payload: { application: { name: string } }) => setStatus(`${payload.application.name} 已连接`))
      .catch(() => setStatus("应用服务暂不可用"));
  }, []);

  return (
    <main>
      <p className="eyebrow">RAG PARSE</p>
      <h1>可信文档问答平台</h1>
      <p>{status}</p>
      <p>后续将在此接入登录、知识库与可追溯检索。</p>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
