# 先兆医学 · predictive_medicine

`predictive_medicine`（原 `rag_parse`）是一个正在建设的开源**个人行为先兆预判 / 基线漂移解释 Agent**。系统拟将经过授权的日常观测整理为个人时间线，识别相对于个人情境化基线的变化，结合历史与上下文生成可追溯的线索，交由人复核。

这里的“先兆预判”指**较早发现值得复核的变化**。项目当前不提供疾病诊断、病因判断、治疗建议或经过临床验证的未来风险预测。原型的分析结果不能用于紧急处置。

## 目标链路

```text
授权观测（首版 CSV/JSON 与模拟记录；后续 HealthKit/语音）
  → 时间对齐、质量与缺失检查
  → 多时间窗口个人基线
  → 统计漂移和变点检测
  → 历史相似片段、上下文与证据
  → 受控 Agent 生成待复核线索
  → 人工复核、结果回写与离线评测
```

数值检测由可测试的统计逻辑负责；Agent 负责查询经过授权的证据、整理不确定性并生成复核案例。计划用 Python 构建核心能力，以 LangGraph 编排有限步骤，以 LangChain 接入模型、消息和工具。PostgreSQL 保存业务真相；Qdrant 仅在需要时辅助检索历史相似事件，不能替代时间序列基线计算。

## 架构与职责边界

整体采用**模块化单体 + 用例驱动分层 + 端口/适配器边界 + 选择性 DDD**。先在一个 Python 后端中建立清晰边界；业务规则稳定且复杂时，再引入领域实体、值对象等 DDD 技法。当前优先建设后端，前端和 BFF 暂不推进。

按业务能力逐步形成授权与数据治理、观测导入、数据质量、基线/漂移、证据与复核等模块。每个模块遵守以下职责边界：

| 边界 | 职责 |
| --- | --- |
| App / API | `app/` 承载 FastAPI 应用装配与 HTTP 接入；`app/api/` 接收请求、校验格式、调用 Service、返回结果 |
| Service | 完成业务用例：检查身份、主体、授权和用途，协调取数、规则计算、事务、持久化及审计 |
| 纯业务规则 | 独立计算覆盖率、基线、漂移和状态变化；不依赖 HTTP、数据库或模型，可用合成数据测试。当前可放在 Service 下的独立文件或子目录 |
| Repository | 数据库查询与持久化，按经过验证的主体/授权范围约束访问；不决定漂移结论、阈值或是否允许外发 |
| Adapter | 文件、模型、语音、对象存储、Qdrant 等外部能力的具体接入；数据库持久化由 Repository 承接 |
| Agent | 编排受控工具和业务用例，整理证据与不确定性；工具通过 Service 访问数据，不能绕过权限和检测规则 |
| Config | `config/` 只存 YAML；`common/config/` 负责读取、环境变量替换、模型校验、缓存及启动配置装配；密钥通过环境或受控密钥配置提供 |
| Observability | 结构化日志、运行事件、指标与调用追踪；Langfuse 等接入放在这里，记录内容受脱敏和外发策略约束 |
| Common | 少量无业务归属的通用工具；业务规则和外部调用不放入 Common |

`API → Service → Repository` 表示职责分工，不要求每次操作都访问数据库。Agent 工具、后台任务和后续离线入口都应复用同一套 Service 授权与业务规则。`logs/` 若使用，仅保存运行产物，日志配置和采集代码归入 Observability。

## 后端目录与应用装配

以下是目标结构，包含尚未实现的扩展位置，不代表目录中的能力已经可用。包目录中的 `__init__.py` 在图中省略。

```text
backend/
├── main.py                         # 唯一启动入口，启动 Uvicorn
├── app/                            # FastAPI 接入与应用装配
│   ├── factory.py                  # create_app(config)，创建应用
│   ├── lifespan.py                 # 初始化、关闭运行资源
│   ├── resources.py                # 连接池、HTTP 客户端等资源集合
│   ├── api/
│   │   ├── router.py               # 汇总模块 Router
│   │   ├── health.py               # 健康检查
│   │   ├── observations/           # 观测导入、查询
│   │   ├── baselines/              # 基线计算、查询
│   │   ├── drifts/                 # 漂移检测、结果查询
│   │   ├── reviews/                # 人工复核、反馈
│   │   ├── conversations/          # 会话接口，设计暂缓
│   │   ├── runs/                   # 执行、取消及流式事件接口
│   │   ├── voice/                  # 音频上传、转写、语音回复
│   │   └── documents/              # 文档上传、解析状态、引用
│   ├── dependencies/              # 提供身份、运行资源、Service
│   ├── middleware/                # 请求 ID、请求上下文等 HTTP 中间件
│   ├── exception/                 # 业务异常到 HTTP 响应的映射与注册
│   └── schema/                    # 通用错误、分页等 HTTP 数据结构
├── service/                       # 业务用例与可独立测试的规则
├── repository/                    # 查询、持久化
├── agent/                         # LangGraph 编排、受控工具
├── adapter/                       # 模型、语音、文件等外部能力接入
├── observability/                 # 日志、指标、追踪及 Langfuse
├── common/config/
│   ├── loader.py                  # YAML 读取、环境变量替换，返回字典
│   ├── manager.py                 # 按模型加载、校验及缓存
│   ├── bootstrap.py               # 集中加载启动配置，返回 BatchConfig
│   └── model/                     # 按配置类别定义 Pydantic 模型
├── config/                        # server.yaml 等 YAML 数据文件
└── tests/
```

`app/` 不再作为全部后端代码的总容器。业务逻辑归入 Service，持久化归入 Repository，Agent 编排归入 Agent；这些模块不依赖 FastAPI 的 `Request`、`APIRouter` 等 HTTP 类型。当前不额外增加 `gateway/`，也不要求为使用 LangGraph 引入 Aegra。

接口在 `app/api/` 内按业务领域或能力划分。简单模块可先用单个文件；内容增加后，再拆为 `router.py`、`schemas.py` 等。请求和响应模型属于接口契约，不是数据库实体。SSE、WebSocket 等接入代码归入对应接口模块，并复用同一套 Service。尚未实现的业务模块不注册为可用接口。

应用装配分工：

| 位置 | 职责 |
| --- | --- |
| `common/config/bootstrap.py` | 调用 Manager，集中加载启动所需配置；不创建数据库连接或 Agent |
| `app/factory.py` | 接收 `BatchConfig`，创建 FastAPI，注册生命周期、中间件、异常处理和总路由；不在模块导入时连接外部服务 |
| `app/lifespan.py` | 管理资源创建与释放，初始化失败时清理已创建的资源 |
| `app/resources.py` | 定义运行资源集合；与仅承载配置值的 `BatchConfig` 分开 |
| `app/dependencies/` | 从应用资源及请求中提供身份、资源与 Service；数据授权规则仍由 Service 执行 |
| `app/exception/` | 将已知业务异常转换为 HTTP 状态码和错误响应，不向调用方暴露内部堆栈或凭据 |

配置与启动的目标调用顺序：

```text
backend/main.py
  → load_batch_config()
  → create_app(config)
  → Uvicorn 使用配置中的 host、port 启动
  → lifespan 初始化运行资源
  → 接收请求
  → 关闭时释放运行资源
```

配置在启动装配时统一加载，再传给应用工厂。Manager 根据配置模型的 `__config_key__` 选择 YAML，调用 Loader 和 Pydantic 校验，并缓存配置对象。新增配置类型时增加对应模型和 Bootstrap 装配项，无需修改 Manager 的通用加载逻辑。当前 Loader 支持 `${NAME}`、`${NAME:-default}` 替换，但不会自动读取 `.env` 文件。

全局接口前缀只在工厂注册总路由时添加一次，各业务 Router 只定义自身路径。例如默认前缀 `/predictive/medicine` 与健康接口 `/health` 组合为 `/predictive/medicine/health`。前缀设置不会自动改变 `/docs` 或 `/openapi.json`，这些路径如需调整应显式配置。

完成包导入和工厂接入后，统一从项目根目录执行 `python -m backend.main`，项目内部绝对导入使用 `backend.` 前缀。当前阶段先验收启动、配置生效、健康接口、请求追踪和异常处理，再按模块增加业务能力。

## 模型与 Agent 运行边界

上层按任务能力调用统一的模型入口，由配置选择本地或经批准的外部模型。调用层逐步支持超时与取消、受限重试/降级、并发控制、输出校验、用量预算和脱敏追踪。LiteLLM 可作为进程内 Adapter 接入多 Provider，无需为此强制增加独立代理服务。

外发判定必须先于模型路由和降级：本地模型失败不能自动把个人记录发送到云端。数据访问规则同样适用于语音、检索和可观测服务。

LangChain/LangGraph 提供模型、工具、中间件及暂停/恢复机制；DeepAgents 可按需提供子 Agent、文件工具和沙箱接入。框架的审批、文件权限或沙箱不能代替本项目的身份、同意/撤回、主体隔离和数据外发检查。初期只开放经过授权检查的业务工具，不开放任意 Shell 或文件读写；出现不可信代码执行需求后再配置隔离沙箱及网络、文件和凭据边界。

多 Agent 是可选扩展：先验证单一受控流程；只有角色拆分带来可测量的质量收益，才增加权限不同的子 Agent。数值检测始终由可测试的统计逻辑负责。

## 模块顺序

| 模块 | 重点 |
| --- | --- |
| 00–01 | 工程与用途边界、身份授权、撤回和数据策略 |
| 02–03 | 观测事件导入、覆盖率与数据质量 |
| 04–05 | 个人基线、漂移与变点检测 |
| 06–07 | 历史证据和人工复核闭环 |
| 08–09 | 受控 Agent、回放与评测 |
| 10–11 | 现实数据/语音适配、可选多 Agent |
| 12 | 文档解析与知识引用：最后接入照护记录、报告和指南 |

文档解析保留为最后一个独立模块。它为解释提供带原文定位的知识证据，不参与个人数值基线或漂移检测。

## 当前进度

新方向目前处于规划与后端骨架整理阶段。以上描述的是目标架构，尚未全部实现：

- 已有 `server.yaml`、Loader、Manager、`ServerSettings` 与返回 `BatchConfig` 的配置装配函数；根启动入口已将配置中的 host、port 传给 Uvicorn。
- `app/` 正在按上述职责整理，当前已有健康接口及资源、生命周期、依赖、中间件、异常、通用数据结构等文件或包的占位。现有工厂占位文件名为 `factor.py`，目标命名为 `factory.py`，尚未实现应用工厂。
- 旧的 `app/main.py`、`app/config.py`、`app/logging.py`、`app/domain/` 和 RAG bootstrap 接口已从当前工作目录移除；根 `backend/main.py` 仍引用已移除的 `backend.app.main`，需要接入新工厂后才能按当前源码完成启动验收。配置加载成功不等于应用装配完成。
- 全局路由前缀、总 Router 与新工厂尚待接通。Docker 仍使用旧 `app.main:app`；依赖声明尚未包含 Loader 使用的 PyYAML，打包、容器与测试导入路径也需随入口一起对齐。
- `service/`、`repository/`、`agent/`、`observability/` 目前主要是占位包。当前没有个人观测、基线、漂移检测、HealthKit、语音或复核闭环实现；旧测试仍引用已移除的模块和 RAG bootstrap 接口，需要按新结构调整，不能作为新基座已通过验收的证据。

下一步先完成 FastAPI 应用工厂、总路由、配置注入及生命周期等基座，统一入口、导入、容器和验证方式；基座验收后进入授权与数据策略，再用合成数据实现观测导入用例，逐模块建设。开发与评测首先使用合成或许可适用的去标识数据；真实个人记录需要先完成授权、撤回、存储与删除机制。

旧项目的[安全与模型外发策略](docs/security-and-model-policy.md)保留为历史安全基线。其默认拒绝外发、最小权限和审计原则可复用；原文中的知识库、核物理资料和 BFF 阶段安排不是当前开发顺序。

详细现行规划及新线程交接稿保存在本机 `temp/个人行为先兆预判Agent/`。`temp/` 当前不纳入 Git，因此仓库公开版以本 README 为项目入口；落地细节以当前仓库代码和实际测试为准。
