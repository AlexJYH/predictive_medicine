# rag_parse

面向核物理研究所内网资料的文档解析、可追溯 RAG 检索与受控 Agent 系统。

当前已确定的安全与模型外发基线见 [安全与模型外发策略](docs/security-and-model-policy.md)。开发环境只使用无敏感测试资料和 mock 模型。

## 本地启动

复制 `.env.example` 为 `.env`，仅填写本地开发凭据；不要写入真实模型密钥或受限资料。随后运行：

```bash
docker compose up --build
```

- Web：<http://localhost:5173>
- BFF 健康检查（容器内）：`http://bff:3000/health`
- Core API 健康检查（容器内）：`http://api:8000/api/v1/health`

前端通过 BFF 的 `/bff/` 路由访问应用数据；Core API 不向宿主机暴露端口，避免绕过业务权限、审计和模型外发策略。BFF 只做 UI 数据封装与聚合，不能取代 Core 的安全决策。
