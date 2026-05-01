# Major Compass

高中生专业选择决策支持系统。

## 架构概览

```
frontend/          Next.js 14 (App Router) + TypeScript
backend/           FastAPI (Python 3.12) + SQLAlchemy 2.0 async
  ├── api/v1/      REST 接口层（仅做参数校验和路由分发）
  ├── services/    业务逻辑层（不依赖 HTTP 框架，纯函数为主）
  ├── models/      SQLAlchemy ORM 模型
  ├── schemas/     Pydantic v2 请求/响应模型
  └── workers/     Celery 后台任务（爬虫、NLP）
data/
  └── seed/        初始化数据（专业目录、院校列表）
```

## 数据库

| 组件       | 用途                               |
|------------|------------------------------------|
| PostgreSQL | 主数据库（用户、测评、专业、院校）   |
| Redis      | 缓存 + Celery 任务队列              |
| Neo4j *    | 专业→技能→职业 知识图谱（v2 规划）  |

\* v1 不启用，专业-职业关系用 PostgreSQL 简单关联表先行覆盖。

## 快速启动（本地开发）

```bash
cp .env.example .env
docker compose up -d postgres redis
cd backend && pip install -e ".[dev]"
alembic upgrade head
python data/scripts/seed.py
uvicorn app.main:app --reload
# API 文档: http://localhost:8000/docs
```

前端：
```bash
cd frontend && npm install && npm run dev
# http://localhost:3000
```

全栈（含 worker）：
```bash
docker compose up
```

## 测试

```bash
cd backend && pytest -v
```

核心评分逻辑（`app/services/scoring.py`）为纯函数，无需数据库即可测试。

## API 版本策略

所有接口以 `/api/v1/` 为前缀。  
Breaking change → 新增 `/api/v2/`，`v1` 保留至少一个主版本周期。  
Non-breaking 新增字段直接在现有版本中添加（Pydantic 默认忽略未知字段）。

## 关键设计决策

**测评 Session 设计**  
Session 在用户打开第一题时即创建，答题逐条写入 `assessment_responses`，
完成时才计算分数并写入 `assessment_sessions.score_*`。这样：
- 用户可以中途退出后继续（前端带 `session_id`）
- 不同算法版本的结果可以回溯对比
- A/B 测试新的推荐权重时，旧数据不受影响

**专业 RIASEC Profile**  
存为 6 个 `DECIMAL(3,2)` 列，而不是 JSON。  
原因：DB 层可直接计算余弦相似度（PostgreSQL 支持向量运算扩展 `pgvector`，v2 可接入）；
列级索引和类型约束比 JSON 字段更严格。

**软删除 vs 硬删除**  
专业目录条目使用 `is_active` 标志（软删除），不物理删除。  
原因：历史测评结果引用了 `major_id`，硬删除会破坏外键完整性。

**Service 层无框架依赖**  
`app/services/scoring.py` 只包含纯函数，不导入 FastAPI 或 SQLAlchemy。  
这使得单元测试不需要启动数据库或 HTTP 服务器。

## 路线图

| 版本 | 目标                                           |
|------|------------------------------------------------|
| v1   | 测评引擎 + 专业目录匹配 + 院校查询（当前）     |
| v1.1 | 知乎评论爬虫 + 情感标签展示                    |
| v1.2 | 小红书爬虫 + NLP 关键词提取                    |
| v2   | Neo4j 知识图谱 + 技能树可视化                  |
| v2.1 | 就业数据接入 + 薪资/升学率展示                 |
