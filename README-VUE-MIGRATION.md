# 半夏小筑：Vue 3 + FastAPI 整体迁移方案

## 原则

- 迁移期间保持 `main` 分支和当前 Hugo/Cloudflare Pages 生产站点不变。
- 所有新工作先放在 `vue-migration` 分支，验收后再合并。
- Hugo 的 `content/`、`static/` 和旧文章 URL 是迁移源；不删除原始内容。
- Cloudflare Worker `banxia-content-admin` 暂时保留，不直接改造其 OAuth 和 GitHub 写入流程。
- Vue 静态前端最终部署到 Cloudflare Pages；FastAPI、PostgreSQL 继续部署在阿里云，API 域名为 `api.banxia.xin`。

## 目录

- `frontend/`：Vue 3、TypeScript、Vite、Vue Router、Pinia、Element Plus、Axios。
- `backend/`：FastAPI、SQLAlchemy 2、Alembic、PostgreSQL、Argon2。
- `scripts/migrate_hugo_content.py`：非破坏式导出 Hugo Page Bundles 和 static 资源。

## 数据边界

Hugo 文章正文迁移到 Vue 静态内容目录；PostgreSQL 仅保存用户、会话、评论、点赞和收藏。互动数据用文章 slug 关联，避免把正文复制进数据库。

## 开发和验收顺序

1. 运行内容迁移脚本，核对文章/项目/简历数量、正文、图片、Shortcodes、日期、标签和 URL。
2. 本地构建 Vue：进入 `frontend` 执行 `npm install` 和 `npm run build`。
3. 后端在测试数据库运行 Alembic：`cd backend && alembic upgrade head`。
4. 完成注册、登录、会话续期/退出、CSRF、CORS、评论回复、点赞、收藏、个人中心测试。
5. 为 Vue history 路由配置 SPA fallback；为旧 URL 配置兼容和必要重定向。
6. 完成 SEO（title/description/canonical/OG）、sitemap、robots、RSS 替代方案、404、移动端、键盘可访问性测试。
7. 在 Cloudflare Pages 预览环境验证；全部通过后才修改生产 Pages 构建配置并切换。

## 当前实现状态

这是第一阶段的可审查开发底座，不是已上线版本。Vue 页面、路由、内容导出脚本和 FastAPI MVP 基础已加入分支；尚未完成本地依赖安装/构建、真实 Hugo 内容迁移结果核对、Alembic 实库迁移、完整联调、安全测试和生产部署。不得将预览数据视为已迁移的真实内容。

## 后端环境变量

参考 `backend/.env.example`。部署时优先复用现有服务器的 PostgreSQL 服务和安全网络，不公开 5432/8000；仅 Nginx 对外提供 443。不要覆盖现有服务器 `/opt/banxia-api/.env`，也不要把密钥提交到 Git。
