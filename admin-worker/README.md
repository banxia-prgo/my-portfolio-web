# 半夏小筑内容管理 Worker

这是与 Hugo 静态站点分离的 Cloudflare Worker 管理后台。GitHub 作为内容存储，Cloudflare Pages 在 main 更新后负责重新构建站点。

## 功能范围

- GitHub OAuth 登录，仅放行 `ALLOWED_GITHUB_LOGIN` 指定账号。
- 会话存放于 Cloudflare KV，浏览器只保存 HttpOnly、Secure、SameSite=Lax 的签名会话 ID。
- 新建文章和项目、读取/修改简历 Markdown、查看内容列表、上传图片至 `static/uploads/`。
- GitHub API 提交内容；Pages 已连接仓库时会按其配置自动构建。
- 输入大小、路径和图片类型校验；CSP、no-store、拒绝跨站 API 请求。

## 重要说明

此版本是首个可部署的 MVP。发布操作会提交到配置的 Git 分支（默认 main），因此会触发生产构建；编辑器预览目前是安全的纯文本预览，不等同于完整 Hugo 预览。建议先在测试分支/Cloudflare Preview 部署验收，再把 `GITHUB_BRANCH` 改为 main。图片提交到 GitHub 仓库而非 R2，以便保留在现有 Hugo 构建流程内。

## 部署步骤

1. 在 Cloudflare 创建一个 KV namespace，名称例如 `BX_ADMIN_SESSIONS`，把 namespace ID 填入 `wrangler.toml` 的 `id`。
2. 在 GitHub Developer Settings → OAuth Apps 创建 OAuth App：
   - Homepage URL: `https://admin.banxia.xin`
   - Authorization callback URL: `https://admin.banxia.xin/auth/callback`
3. 进入 `admin-worker` 目录，安装 Wrangler（本地已安装时跳过）并部署：

   ```bash
   npm install --global wrangler
   npx wrangler kv namespace create BX_ADMIN_SESSIONS
   # 将输出的 id 填入 wrangler.toml
   npx wrangler secret put GITHUB_CLIENT_ID
   npx wrangler secret put GITHUB_CLIENT_SECRET
   npx wrangler secret put SESSION_SECRET
   npx wrangler deploy
   ```

   `SESSION_SECRET` 使用至少 32 字节随机值。OAuth App 的 Client ID 虽非秘密，但放在 secret 中便于配置一致。
4. 在 Cloudflare Worker Settings → Domains & Routes 绑定 `admin.banxia.xin`。如果域名未接入 Cloudflare DNS，先添加 DNS 记录。
5. GitHub OAuth App 的 callback 必须与绑定域名完全一致。Worker 默认只允许 GitHub 登录名 `banxia-prgo`，如有变化需同步修改变量。
6. 给 GitHub OAuth App 授予私有仓库内容写权限（传统 OAuth App 的 repo scope 较宽）。更严格的生产部署建议改用 GitHub App，并只授予目标仓库 Contents: Read and write。
7. 在 Cloudflare Pages 确认仓库集成、生产分支 main、构建命令 `hugo --gc --minify`、输出目录 `public`。官方 Hugo Pages 指南：https://developers.cloudflare.com/pages/framework-guides/deploy-a-hugo-site/

## 验证

在本地运行 Worker 开发模式：

```bash
npx wrangler dev
```

未配置 secrets 时，`/auth/login` 应返回清晰的配置错误；未登录请求 `/api/content/list` 应返回 401。完成 OAuth 和 KV 配置后，使用授权账号登录，先在非生产分支验证内容写入、图片地址和 Hugo 构建，再切换生产分支。

## 限制与后续工作

- 简历管理编辑现有 `content/resume/_index.md`；PDF 简历替换、R2 图片存储、GitHub App 最小权限授权、真正的 Hugo Preview Deployment、内容删除/回滚暂未启用。
- 不要将 Client Secret、SESSION_SECRET 或访问令牌写入仓库、前端代码或聊天。
- 这个 Worker 与 Pages 是两个独立部署单元。仅合并代码不会自动创建 KV、OAuth App、DNS 记录或部署 Worker。
