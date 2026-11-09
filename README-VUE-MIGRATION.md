# 半夏小筑：Vue 3 + FastAPI 项目架构

本仓库当前正式技术栈为 Vue 3 + TypeScript + Vite、FastAPI、SQLAlchemy、Alembic 和 PostgreSQL。旧 Hugo 站点已停止作为部署目标，仓库不再保留旧 Hugo 主题、模板、构建产物或 Cloudflare 部署配置。

## 部署架构

- 前端：构建为静态资源，部署到阿里云轻量应用服务器，由 Nginx 托管。
- 后端：FastAPI 通过 Docker Compose 运行。
- 数据库：PostgreSQL 运行在服务器内部网络，不直接对公网开放。
- 域名：网站 https://www.banxia.xin/ ，API https://api.banxia.xin/ 。
- 内容与图片：由当前前后端系统管理；用户上传文件保存在服务器持久化目录。

## 目录

- `frontend/`：Vue 3、TypeScript、Vite、Vue Router、Pinia、Element Plus、Axios。
- `backend/`：FastAPI、SQLAlchemy 2、Alembic、PostgreSQL。
- `docs/`：项目技术文档。
- `.github/workflows/backend-check.yml`：后端检查。
- `.github/workflows/vue-migration-ci.yml`：前端及迁移相关 CI 检查。
- `.github/workflows/deploy-frontend.yml`：阿里云前端部署。

## 本地检查

前端：

```bash
cd frontend
npm ci
npm run build
```

后端：

```bash
cd backend
pip install -r requirements.txt
```

后端环境变量参考 `backend/.env.example`。不要提交生产密钥。

## 生产安全约定

1. 不要覆盖服务器上的生产 `.env`。
2. 数据库迁移前先备份，并审查 Alembic 迁移脚本。
3. PostgreSQL 不对公网开放，API 通过 Nginx HTTPS 入口访问。
4. 用户上传文件必须保存在持久化目录，不能随容器重建而丢失。
5. 发布前检查 GitHub Actions 结果；工作流合并不代表生产部署已经完成。
