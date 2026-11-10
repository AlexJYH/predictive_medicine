# 个人行为先兆预判 · predictive_medicine

`predictive_medicine`（原 `rag_parse`）是正在建设的开源**个人行为先兆预判 / 基线漂移解释 Agent**。目标是较早发现个人日常行为相对自身基线的变化，生成带来源、带不确定性、供人复核的线索。

项目不做疾病诊断、因果断言或未经验证的未来风险预测。数值异常由确定性或统计程序检测，LLM 负责整理证据和解释；数据不足时明确输出未知。

## 目标链路

```text
授权观测
  → 时间对齐、质量与缺失检查
  → 多时间窗口个人基线
  → 确定性 / 统计漂移检测
  → 历史相似片段与上下文检索
  → 受控 Agent 生成 ReviewCase
  → 人工复核、Outcome 回写与离线评测
```

首版使用合成或许可适用的去标识数据离线验证。HealthKit、语音、多 Agent 和文档解析为后续能力；文档仅作为照护记录、报告或指南的可选知识源。

技术方向为 Python 后端、LangGraph 有限图编排、LangChain 模型/消息/工具接口。项目自身建设观测契约、基线与漂移证据、授权和模型外发策略、运行事件及回放评测。LangGraph/LangChain 当前尚未接入代码或依赖。

## 当前进度

以下按 2026-11-10 当前源码整理，代码存在不等于已通过完整集成验收。

| 能力 | 当前状态 |
| --- | --- |
| 应用启动与配置 | 已有 FastAPI 工厂、总路由、YAML 配置、环境文件读取、Pydantic 校验与配置装配 |
| 数据库基础 | 已有异步 SQLAlchemy 资源、启动连接检查、Alembic 迁移、雪花 ID、审计及租户查询范围钩子 |
| 用户与租户 | 已有用户、租户、成员关系三表的迁移/ORM、查询及写入方法 |
| 注册与凭据校验 | 已有三表同事务注册、Argon2 密码哈希与校验、用户/租户/成员有效性查询 |
| 请求身份 | 已有 ASGI 认证中间件、配置化公开路由及 ContextVar 身份上下文；dev 使用 Header 并查询数据库验证身份 |
| Token 会话 | 仅有验证协议和中间件调用位置；工厂传入 `token_verifier=None`，Token 签发、验证实现、Redis 会话和过期/注销尚未完成 |
| 管理权限与开户限制 | 尚无完整管理角色/权限校验；`register` 可重复调用，一次性初始化限制已决定暂缓 |
| 个人数据授权 | ConsentGrant、撤回及模型外发策略尚未落地；用户租户身份不能替代个人数据授权 |
| Agent 与核心业务 | `agent/` 为空包；观测、质量、基线、漂移、证据、ReviewCase、Outcome 与回放评测尚未实现 |
| 工程验收 | Docker 和旧测试仍引用历史入口，需要对齐；当前不能视为生产就绪 |

当前主线已进入最小 Agent 运行结构设计：先明确一次 Run 的用例、输入输出及状态，再定义最小数据契约和必要能力协议，随后接入 LangGraph/LangChain。可先用固定合成证据验证解释链；完整业务闭环仍需逐步补齐观测、质量、基线和漂移检测。

## 代码结构与职责

采用模块化单体，主要调用关系为 `API → Service → Repository`。Service 协调用例、身份授权和事务，Repository 负责查询与持久化；未来统计规则独立于 HTTP、数据库和 LLM，Agent 工具通过 Service 访问受控能力。

```text
backend/
├── main.py                         # 配置加载、迁移、Uvicorn 启动
├── app/
│   ├── factor.py                   # 当前实际文件名：应用工厂与 lifespan
│   ├── api/
│   │   ├── router.py               # 汇总路由
│   │   ├── health/health.py        # 带身份的数据库写入检查
│   │   └── identity/identity.py    # 注册、凭据校验、创建租户
│   ├── middleware/authentication/ # 身份解析、拒绝响应、Token 验证协议
│   ├── dependencies/
│   ├── exception/
│   └── schema/
├── services/                       # health、identity 用例与契约
├── repository/                     # ORM、仓储协议、PostgreSQL 实现
├── infrastructure/
│   ├── database/                   # Session、审计、租户范围与连接检查
│   └── runtime.py                 # 运行资源注册与获取
├── common/
│   ├── config/                    # Loader、Manager、Bootstrap、配置模型
│   ├── identity/                  # IdentityContext 与上下文操作
│   ├── id/                        # 雪花 ID
│   └── secuirty/password.py        # 当前拼写如此，Argon2 哈希与验证
├── config/                        # YAML 配置
├── env/example/                   # 本地环境文件模板
├── migrations/versions/            # 健康记录与身份三表迁移
├── agent/                         # 待建设
├── observability/                 # 可观测能力扩展位置
└── tests/                         # 历史测试，待适配当前结构
```

`factor.py` 已实现工厂，生命周期目前也定义在这个文件内。部分其他目录只有占位，目录存在不表示相关功能已完成。内部绝对导入使用 `backend.` 前缀。

## 本地启动

需要 Python 3.12+、uv 和可连接的 PostgreSQL。以下命令从项目根目录执行。

```bash
uv sync --project backend --no-install-project
```

当前 setuptools 尚未配置平铺多包发现，直接 `uv sync --project backend` 会尝试安装项目并报 `Multiple top-level packages discovered`。上述命令安装依赖并跳过项目自身安装；项目包名和描述仍保留历史 RAG 命名。

首次配置环境目录（已有 `backend/env/dev/` 时保留现有文件）：

```bash
mkdir -p backend/env/dev
cp -n backend/env/example/*.env backend/env/dev/
```

编辑其中的 `.env` 文件，替换模板中的 `******`。数据库连接使用 `DATABASE_URL=postgresql+asyncpg://用户名:密码@主机:端口/数据库名`；服务配置可使用：

```ini
PREDICTIVE_MEDICINE_PREFIX=/predictive/medicine
PREDICTIVE_MEDICINE_HOST=127.0.0.1
PREDICTIVE_MEDICINE_PORT=8001
```

启动前确保数据库已存在且连接账号有迁移所需权限：

```bash
APP_ENV=dev backend/.venv/bin/python -m backend.main
```

`APP_ENV` 必须显式设置，用于选择 `backend/env/<环境>/`，认证中间件也据此选择身份模式。配置装配读取该目录内的 `*.env`，同名变量由进程环境覆盖；YAML 支持 `${NAME}` 和 `${NAME:-default}` 替换。IDE 使用本项目 `backend/.venv/bin/python`，工作目录设为项目根目录，并设置 `APP_ENV=dev`。

当前启动顺序为：

```text
加载环境与 YAML 配置 → create_app
  → Alembic upgrade head
  → 启动 Uvicorn
  → lifespan 创建数据库资源并执行连接检查
  → 注册运行资源、完成 startup、接收请求
  → 关闭时清理资源并释放数据库连接
```

**运行入口会自动执行待应用迁移并修改数据库结构。** 连接检查在 lifespan 的 `yield` 前完成；迁移或检查失败会阻止完成启动。当前 Dockerfile 仍使用旧 `app.main:app` 且未复制完整后端，尚不能作为当前版本部署入口。

## 当前接口与身份规则

默认全局前缀为 `/predictive/medicine`，仅在总路由注册时添加一次。

| 方法 | 完整路径 | 身份要求与行为 |
| --- | --- | --- |
| POST | `/predictive/medicine/identity/register` | 匿名注册；创建租户、用户及成员关系，返回 ID、用户名和邮箱，不签发 Token |
| POST | `/predictive/medicine/identity/verify` | 匿名提交用户名、密码、tenant_id；成功返回 IdentityContext，不签发 Token |
| POST | `/predictive/medicine/identity/create_tenant` | 要求请求身份；创建租户，尚未补管理权限校验或自动成员绑定 |
| POST | `/predictive/medicine/check/health` | 要求请求身份；事务写入健康检查记录并返回结果，会产生数据库数据 |

公开路由由 `backend/config/white_list.yaml` 中的 `method + path` 精确配置；配置路径不含全局前缀，由工厂拼接。当前仅注册和凭据校验公开，注册没有一次性限制，也没有赋予“默认管理员”的权限模型。

身份模式互斥：

- **dev**：传入完整的 `X-Tenant-Id` 和 `X-User-Id`，中间件通过 Service 查询有效用户、租户及成员关系，再设置 IdentityContext；这用于本地开发，Header 本身不能证明请求者身份。
- **非 dev**：设计为仅接收 `Authorization: Bearer <token>`；当前缺少验证实现，尚不可作为可用认证链路。
- Token 与身份 Header 不可同时传递；重复身份 Header 会被拒绝。业务通过 `require_identity()` 读取经过中间件设置的上下文，匿名公开请求没有该上下文。

使用数据库内已有且有效的成员 ID 测试健康接口：

```bash
curl -X POST http://127.0.0.1:8001/predictive/medicine/check/health \
  -H 'X-Tenant-Id: <真实租户ID>' \
  -H 'X-User-Id: <真实用户ID>'
```

请求字段以 `backend/services/identity/model/common.py` 为准。当前可空字段未设置默认值，不能把“允许 null”理解为“可以省略”；必填约束仍需完善。缺失/非法身份 Header、认证失败和数据库冲突的受控错误响应也尚未完整覆盖，可能返回 500。

`verification_timeout_seconds` 位于 `backend/config/identity.yaml`，单位为秒，表示单次 Token 验证等待上限，**不是 Token 有效期**。Redis 会话 TTL、过期与注销为后续工作。

FastAPI 保留默认 `/docs` 与 `/openapi.json` 路径，但当前认证中间件同样会处理这些路径；它们没有自动列入公开路由。

## 数据库迁移与验证

迁移配置为 `backend/alembic.ini`，现有版本包括健康记录表和身份三表。手动查看历史或执行迁移时，也从项目根目录使用后端解释器：

```bash
APP_ENV=dev backend/.venv/bin/python -m alembic -c backend/alembic.ini history
APP_ENV=dev backend/.venv/bin/python -m alembic -c backend/alembic.ini current
APP_ENV=dev backend/.venv/bin/python -m alembic -c backend/alembic.ini upgrade head
```

后两条需要数据库连接，`upgrade head` 会修改数据库。已应用版本不会因编辑旧脚本而重新执行；结构变更新建迁移。自动生成迁移前还需确认 `env.py` 导入了全部受管理 ORM，避免仅加载 Base 得到不完整 metadata。

数据库已有针对 `BusinessEntityMixin` 的租户/软删除查询范围与审计钩子；身份查询使用限定的 `authentication_query=True` 例外。它们不等同于完整权限体系，事务内 `set_config` 也不等于已实现 PostgreSQL RLS。

旧测试仍引用已移除的 `app.main` / `app.domain.model_policy`，需要迁移到当前代码；不能用历史测试结果证明当前版本通过。下一阶段应补身份拒绝路径、注册事务回滚、租户隔离和最小 Agent 运行的验收样例。

## 后续实施与文档

| 模块 | 重点 |
| --- | --- |
| 00 | 工程、数据库、异常与可复现验证 |
| 01A / 01B | 用户租户认证；个人授权、撤回与外发策略 |
| 02–03 | 观测导入、时间对齐、覆盖率与数据质量 |
| 04–05 | 个人多窗口基线、确定性/统计漂移 |
| 06–07 | 历史证据、ReviewCase、人工决定与 Outcome |
| 08–09 | 受控 Agent 运行、事件、回放与离线评测 |
| 10–12 | 现实数据/语音、可选多 Agent、文档知识源 |

可先设计最小 Run 契约并用合成 EvidencePacket 验证有限图，但不得把模型生成解释当作数值检测已完成。模型外发、工具访问和恢复执行均需独立授权；真实个人数据接入前落实同意、撤回、存储与删除规则。

本地详细资料位于 `temp/`：`个人行为先兆预判Agent/` 为规划与模块任务书，`待办/` 为分模块缺口清单，`project-memory.md` 记录最新决策，`项目推进时间表-每天两小时.md` 为排期参考。`temp/` 被 Git 忽略，公开仓库以本 README 和实际代码为入口；历史计划有冲突时以最新决策为准。

旧的[安全与模型外发策略](docs/security-and-model-policy.md)保留为历史参考，其最小权限、默认拒绝外发与审计原则可复用；原 RAG 产品范围和实施顺序不再是当前主线。
