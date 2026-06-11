# 赛果先知

2026 世界杯娱乐预测 MVP。网站展示胜平负概率、最可能比分、预期进球、球员状态和可解释因素；Python 服务负责特征计算、双泊松预测、回测和发布。

> 所有预测仅供足球数据研究与娱乐，不构成投注或投资建议。

## 目录

- `web/`：Next.js 网站、详情页、复盘页和只读 API。
- `predictor/`：Python 特征管道、模型、校验、回测和每日任务。
- `database/schema.sql`：PostgreSQL 数据结构。
- `docker-compose.yml`：本地 PostgreSQL。

## 本地运行

要求 Node.js 20+ 与 Python 3.11+。

```powershell
npm --prefix web install
npm run dev
```

打开 `http://localhost:3000`。未设置数据库时，网站使用演示数据。

运行测试与生产构建：

```powershell
npm test
npm run build
```

## 接入 PostgreSQL

```powershell
docker compose up -d
Copy-Item .env.example .env.local
```

将 `DATABASE_URL` 配置到 `web/.env.local`，将 `PREDICTOR_DATABASE_URL` 配置到预测任务环境。数据库不可用时网站会失败关闭到演示数据；预测任务校验失败时不会覆盖上一份有效预测。

## 数据适配器

实现 `predictor/worldcup/sources/base.py` 中的 `MatchSource`，将授权数据标准化为 `MatchContext`。适配器必须：

1. 只读取预测时间点之前 365 天的数据。
2. 保留来源、比赛时间、赛事等级、对手强度和实际分钟数。
3. 不绕过登录、验证码、付费墙或访问控制。
4. 对同名球员使用来源 ID，而不是姓名匹配。

`run_daily` 会先验证阵容，再原子发布预测；同一 `match_id + model_version + data_version` 重跑是幂等的。

## 部署

- Vercel：将 Root Directory 设为 `web`，配置 `DATABASE_URL`。
- PostgreSQL：可使用 Supabase、Neon 或其他兼容服务，执行 `database/schema.sql`。
- Python 任务：部署到 Railway/Render，设置 `PREDICTOR_DATABASE_URL`，用每日 cron 调用包含 `run_daily` 的数据源入口。
- 正式首发或重大伤停更新后，使用新的 `data_version` 额外执行一次任务。

生产环境应监控 `data_runs` 中的失败记录、预测覆盖率和数据更新时间。网页抓取来源在投入公开使用前必须确认授权与展示条款。
