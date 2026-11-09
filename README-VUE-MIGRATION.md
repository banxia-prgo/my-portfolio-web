# 半夏小筑：Vue 3 + FastAPI 整体迁移方案

## 部署原则

- 新站前端和后端统一部署在阿里云轻量应用服务器；前端由 Nginx 静态托管，后端由 Docker Compose 运行。
- 迁移期间保留现有 Hugo/Cloudflare Pages 站点作为回退来源；完成验收前不切换根域名，不删除旧站。
- 所有新工作先放在 `vue-migration` 分支，验收后再合并。
- Hugo 的 `content/`、`static/` 和旧文章 URL 是迁移源；不删除原始内容。
- 不再采用 Cloudflare Worker CMS 作为新站内容管理方案；后续内容更新以 GitHub、本地构建和上传阿里云服务器为准。
- 前端域名为 `www.banxia.xin`，后端 API 域名为 `api.banxia.xin`；根域名是否跳转到 www，待验收后配置。

## 目录

- `frontend/`：Vue 3、TypeScript、Vite、Vue Router、Pinia、Element Plus、Axios。
- `backend/`：FastAPI、SQLAlchemy 2、Alembic、PostgreSQL、Argon2。
- `scripts/migrate_hugo_content.py`：非破坏式导出 Hugo Page Bundles 和 static 资源。
- `scripts/deploy-frontend.sh`：在阿里云服务器上进行前端原子化更新，保留备份并支持失败回滚。

## 数据边界

Hugo 文章正文迁移到 Vue 静态内容目录；PostgreSQL 仅保存用户、会话、评论、点赞和收藏。互动数据用文章 slug 关联，避免把正文复制进数据库。

## 开发和验收顺序

1. 运行内容迁移脚本，核对文章/项目/简历数量、正文、图片、Shortcodes、日期、标签和 URL。
2. 本地构建 Vue：进入 `frontend` 执行 `npm ci` 和 `npm run build`。
3. 后端在独立测试数据库运行 Alembic；生产数据库变更必须先备份、审查迁移脚本并单独执行。
4. 完成注册、登录、会话续期/退出、CSRF、CORS、评论回复、点赞、收藏、个人中心测试。
5. 为 Vue history 路由配置 Nginx SPA fallback；为旧 URL 配置兼容和必要重定向。
6. 完成 SEO（title/description/canonical/OG）、sitemap、robots、RSS 替代方案、404、移动端、键盘可访问性测试。
7. 在阿里云服务器的预发布目录验证构建产物、Nginx 路由、API 联通和回滚流程；全部通过后再发布正式前端。
8. 先验收 `www.banxia.xin`，最后再决定根域名 DNS 和旧 Hugo 站点的下线时间。

## 当前实现状态

这是第一阶段的可审查开发底座，不是已完成验收的上线版本。Vue 页面、路由、内容导出脚本和 FastAPI MVP 基础已加入分支；CI 的前后端基础检查已通过，但真实 Hugo 内容迁移结果核对、完整联调、功能与安全测试、SEO/兼容性验收仍需完成。不得将预览数据视为已迁移的真实内容，也不得在验收前切换生产根域名。

## 后端环境变量与安全边界

参考 `backend/.env.example`。生产部署复用阿里云服务器上受保护的环境变量和 PostgreSQL 服务；数据库不公开 5432，API 仅通过 Nginx 对外提供 HTTPS。不要覆盖现有服务器 `/opt/banxia-api/.env`，也不要把密钥提交到 Git。
