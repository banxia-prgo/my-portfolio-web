# 半夏小筑 Vue 前端

Vue 3 + TypeScript + Vite。此目录是新前端应用，迁移期间不会覆盖原 Hugo 网站。

## 本地开发

```bash
npm install
cp .env.example .env.local
npm run dev
```

默认 API 地址为 `https://api.banxia.xin`，可通过 `VITE_API_BASE_URL` 覆盖。

## 构建

```bash
npm install
npm run build
```

产物位于 `dist/`。正式切换域名前，必须先完成原 Hugo 内容 Page Bundle 的完整迁移、Vue 路由兼容/重定向、FastAPI 认证与互动接口、Cookie/CSRF/CORS 联调、SEO 元数据和移动端测试。当前 `src/data/site.ts` 仅是开发预览数据，不能当作完整内容迁移结果。

## 导入 Hugo 内容

从仓库根目录安装迁移依赖并运行：

```bash
python -m pip install -r scripts/requirements-migration.txt
python scripts/migrate_hugo_content.py
```

脚本只读取 `content/`，将 Markdown 目录和静态资源复制到 `frontend/public/content/`，不会删除或改写 Hugo 源文件。请人工检查 Hugo Shortcodes、复杂图片链接、front matter 和简历内容。

## 目标路由

- `/` 首页
- `/posts/` 随笔归档
- `/posts/:slug/` 随笔详情
- `/projects/` 项目列表
- `/projects/:slug/` 项目详情
- `/resume/` 简历
- `/login/` 登录
- `/register/` 注册
- `/profile/` 个人中心

Vue Router 使用 history 模式，部署服务器需将未知页面路径回退到 `index.html`。旧站点仍保持线上运行，直到迁移验收通过。
