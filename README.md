# 半夏小筑

基于 Vue 3 + TypeScript + Vite 与 FastAPI 构建的个人网站。

线上地址：https://www.banxia.xin/  
API 地址：https://api.banxia.xin/

## 项目结构

- `frontend/`：Vue 3 前端，使用 TypeScript、Vite、Vue Router、Pinia、Element Plus 和 Axios。
- `backend/`：FastAPI 后端，使用 SQLAlchemy、Alembic 和 PostgreSQL。
- `docs/`：架构、媒体存储等项目文档。
- `.github/workflows/`：前后端检查及阿里云前端部署工作流。

## 本地开发

前端：

```bash
cd frontend
npm ci
npm run dev
```

生产构建：

```bash
npm run build
```

后端：

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端环境变量参考 `backend/.env.example`。

## 生产部署

- 前端构建后部署到阿里云服务器，由 Nginx 提供静态文件服务。
- FastAPI 与 PostgreSQL 通过服务器上的 Docker Compose 运行。
- 前端部署通过 GitHub Actions 工作流执行。
- 图片等用户上传文件存储在服务器持久化目录，不应放入前端构建产物或提交到仓库。

## 内容与后台

网站文章、项目、简历及互动功能由当前 Vue 前端和 FastAPI 服务提供。后台内容管理支持内容维护、图片管理及留言审核。生产数据和上传文件保存在服务器端。

