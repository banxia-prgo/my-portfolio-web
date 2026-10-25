const API = "https://api.github.com";
const COOKIE = "__Host-bx_admin";
const SESSION_TTL = 60 * 60 * 8;
const MAX_TEXT = 700_000;
const MAX_IMAGE = 4 * 1024 * 1024;

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...headers } });
}
function html(body, status = 200) {
  return new Response(body, { status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "content-security-policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'", "x-content-type-options": "nosniff", "referrer-policy": "no-referrer", "x-frame-options": "DENY" } });
}
function cookie(name, value, maxAge) {
  return `${name}=${value}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}
function randomHex(bytes = 24) {
  const b = crypto.getRandomValues(new Uint8Array(bytes));
  return [...b].map(x => x.toString(16).padStart(2, "0")).join("");
}
function base64url(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}
async function sign(value, secret) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return base64url(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value)));
}
async function safeEqual(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}
function parseCookies(request) {
  return Object.fromEntries((request.headers.get("Cookie") || "").split(";").map(s => s.trim()).filter(Boolean).map(s => {
    const i = s.indexOf("="); return [s.slice(0, i), s.slice(i + 1)];
  }));
}
function fromBase64url(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  return Uint8Array.from(atob(normalized + "=".repeat((4 - normalized.length % 4) % 4)), ch => ch.charCodeAt(0));
}
async function sessionKey(secret) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(secret));
  return crypto.subtle.importKey("raw", digest, { name: "AES-GCM" }, false, ["encrypt", "decrypt"]);
}
async function sealSession(data, secret) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await sessionKey(secret);
  const plain = new TextEncoder().encode(JSON.stringify(data));
  const encrypted = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, plain);
  return base64url(iv) + "." + base64url(encrypted);
}
async function openSession(value, secret) {
  try {
    const [ivText, encryptedText] = value.split(".");
    if (!ivText || !encryptedText) return null;
    const key = await sessionKey(secret);
    const plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: fromBase64url(ivText) }, key, fromBase64url(encryptedText));
    const data = JSON.parse(new TextDecoder().decode(plain));
    if (!data || typeof data.token !== "string" || typeof data.login !== "string" || !Number.isFinite(data.expires) || data.expires < Date.now()) return null;
    return data;
  } catch {
    return null;
  }
}
async function sessionFor(request, env) {
  const value = parseCookies(request)[COOKIE];
  if (!value) return null;
  if (!env.SESSION_SECRET) {
    console.warn("[auth] session_secret_missing");
    return null;
  }
  const data = await openSession(value, env.SESSION_SECRET);
  if (!data) {
    console.warn("[auth] cookie_invalid_or_expired");
    return null;
  }
  return data;
}
function validOrigin(request, env) {
  const origin = request.headers.get("Origin");
  if (request.method === "GET" || request.method === "HEAD") return !origin || origin === env.ADMIN_ORIGIN;
  return Boolean(origin && env.ADMIN_ORIGIN && origin === env.ADMIN_ORIGIN);
}
function slugify(s) {
  return String(s || "").normalize("NFKC").trim().toLowerCase()
    .replace(/[^\p{L}\p{N}\s_-]/gu, "").replace(/[\s_]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "").slice(0, 80);
}
function frontmatter(title, summary, tags, draft) {
  const q = s => JSON.stringify(String(s || ""));
  return `---
title: ${q(title)}
date: ${new Date().toISOString()}
summary: ${q(summary)}
tags: ${JSON.stringify(tags)}
draft: ${draft ? "true" : "false"}
---

`;
}
async function github(env, token, path, init = {}) {
  const url = path.startsWith("https://") ? path : API + path;
  const res = await fetch(url, { ...init, headers: {
    "accept": "application/vnd.github+json",
    "authorization": "Bearer " + token,
    "x-github-api-version": "2022-11-28",
    "user-agent": "Banxia-Content-Admin",
    ...(init.body ? { "content-type": "application/json" } : {}),
    ...init.headers
  }});
  const text = await res.text();
  let data; try { data = text ? JSON.parse(text) : {}; } catch { data = { message: text.slice(0, 500) }; }
  if (!res.ok) throw new Error(data.message || `GitHub API error ${res.status}`);
  return data;
}
async function putFile(env, token, path, content, message, sha, alreadyBase64 = false) {
  const body = { message, content: alreadyBase64 ? content : btoa(unescape(encodeURIComponent(content))), branch: env.GITHUB_BRANCH || "main" };
  if (sha) body.sha = sha;
  return github(env, token, `/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path.split("/").map(encodeURIComponent).join("/")}`, { method: "PUT", body: JSON.stringify(body) });
}
function safePath(kind, slug, fileName) {
  if (kind !== "resume" && !/^[\p{L}\p{N}][\p{L}\p{N}_-]{0,79}$/u.test(slug)) throw new Error("内容标识不合法");
  if (kind === "post") return `content/posts/${slug}/index.md`;
  if (kind === "project") return `content/projects/${slug}/index.md`;
  if (kind === "resume") return "content/resume/_index.md";
  if (kind === "image") {
    if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,90}\.(png|jpe?g|webp|gif|svg)$/i.test(fileName || "")) throw new Error("图片文件名不合法");
    return `static/uploads/${fileName}`;
  }
  throw new Error("未知内容类型");
}
async function listContent(env, token) {
  const tree = await github(env, token, `/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/git/trees/${env.GITHUB_BRANCH || "main"}?recursive=1`);
  const files = (tree.tree || []).filter(x => x.type === "blob" && /^content\/(posts|projects)\/.+\.md$/i.test(x.path) && !x.path.endsWith("/_index.md"));
  return files.map(x => ({ path: x.path, type: x.path.startsWith("content/posts/") ? "post" : "project", title: x.path.split("/").slice(-2, -1)[0], sha: x.sha })).sort((a,b) => a.path.localeCompare(b.path));
}
const PAGE = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>半夏小筑 · 内容管理</title><style>
:root{color-scheme:light;--ink:#29243b;--muted:#77718b;--line:#e8e3f3;--lav:#8b79d6;--soft:#f3f0ff;--aqua:#e6f7f6}*{box-sizing:border-box}body{margin:0;background:linear-gradient(135deg,#f9f7ff,#f4fbfb);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}button,input,textarea,select{font:inherit}button{cursor:pointer;border:0;border-radius:12px;padding:10px 15px;background:var(--lav);color:white;font-weight:650}button.secondary{background:#eeeaf8;color:var(--ink)}button.danger{background:#a44361}.wrap{max-width:1180px;margin:auto;padding:28px 18px}.top{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:24px}.brand{font-size:23px;font-weight:800;letter-spacing:.02em}.brand small{display:block;font-size:12px;color:var(--muted);font-weight:500}.layout{display:grid;grid-template-columns:220px minmax(0,1fr);gap:20px}.panel{background:#ffffffd9;border:1px solid var(--line);border-radius:20px;padding:20px;box-shadow:0 12px 40px #62529b0b}.nav{display:grid;gap:8px;align-content:start}.nav button{background:transparent;color:var(--muted);text-align:left}.nav button.active{background:var(--soft);color:#5c4aab}.field{display:grid;gap:6px;margin:12px 0}.field label{font-size:13px;color:var(--muted);font-weight:650}input,textarea,select{width:100%;border:1px solid var(--line);border-radius:11px;padding:11px 12px;background:white;color:var(--ink);outline-color:var(--lav)}textarea{min-height:260px;resize:vertical;font:13px/1.65 ui-monospace,SFMono-Regular,Consolas,monospace}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.row>*{flex:1}.hidden{display:none!important}.note{padding:12px 14px;border-radius:12px;background:var(--aqua);color:#365c5a}.muted{color:var(--muted)}.list{display:grid;gap:8px;margin-top:16px}.item{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:12px;border:1px solid var(--line);border-radius:12px;background:white}.status{white-space:pre-wrap;margin:12px 0;color:#6652aa}.editor-head{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}@media(max-width:760px){.layout{grid-template-columns:1fr}.nav{grid-template-columns:repeat(2,minmax(0,1fr))}.wrap{padding:16px 12px}.panel{padding:15px}.top{align-items:flex-start}}
</style></head><body><div class="wrap"><header class="top"><div class="brand">半夏小筑 <small>内容管理后台 · 仅限授权账号</small></div><div id="user" class="muted"></div></header><section id="login" class="panel"><h2>安全登录</h2><p class="muted">使用授权的 GitHub 账号登录后管理网站内容。</p><button id="loginBtn">使用 GitHub 登录</button></section><main id="app" class="layout hidden"><aside class="panel nav"><button class="active" data-tab="post">✦ 技术随笔</button><button data-tab="project">◇ 项目管理</button><button data-tab="resume">▤ 简历资料</button><button data-tab="image">↥ 图片上传</button><button data-tab="browse">☷ 内容列表</button><button id="logout" class="secondary">退出登录</button></aside><section class="panel"><div class="editor-head"><h2 id="heading">新增技术随笔</h2><span class="muted" id="subheading">保存到 GitHub 仓库</span></div><div id="status" class="status" role="status"></div>
<div id="form-post"><div class="field"><label>文章标题</label><input id="postTitle" placeholder="例如：C++ 学习记录"></div><div class="field"><label>URL 标识（英文或中文，留空自动生成）</label><input id="postSlug" placeholder="cpp-learning-notes"></div><div class="field"><label>摘要</label><input id="postSummary" placeholder="用一句话介绍文章"></div><div class="field"><label>标签（逗号分隔）</label><input id="postTags" placeholder="C++, 学习笔记"></div><div class="field"><label>正文 Markdown</label><textarea id="postBody" placeholder="# 开始写作&#10;&#10;支持 Markdown。上传图片后可复制图片地址并插入 ![说明](图片地址)。"></textarea></div><div class="row"><button id="postPreview" class="secondary">预览 Markdown</button><button id="postSave">发布文章</button></div><div id="preview" class="note hidden"></div></div>
<div id="form-project" class="hidden"><div class="field"><label>项目名称</label><input id="projectTitle" placeholder="项目名称"></div><div class="field"><label>URL 标识（英文或中文）</label><input id="projectSlug" placeholder="project-name"></div><div class="field"><label>项目摘要</label><input id="projectSummary" placeholder="项目解决什么问题"></div><div class="field"><label>技术栈（逗号分隔）</label><input id="projectTags" placeholder="C++, Qt, OpenCV"></div><div class="field"><label>GitHub 地址</label><input id="projectRepo" placeholder="https://github.com/..."></div><div class="field"><label>演示地址（可选）</label><input id="projectDemo" placeholder="https://..."></div><div class="field"><label>项目说明 Markdown</label><textarea id="projectBody" placeholder="项目背景、功能、运行方式……"></textarea></div><button id="projectSave">保存项目并发布</button></div>
<div id="form-resume" class="hidden"><p class="note">这里编辑 <code>content/resume/_index.md</code> 的完整 Markdown。请保留现有 front matter，避免覆盖不需要修改的简历内容。</p><div class="field"><label>简历 Markdown（完整文件）</label><textarea id="resumeBody" placeholder="点击下方读取当前简历后编辑"></textarea></div><div class="row"><button id="resumeLoad" class="secondary">读取当前简历</button><button id="resumeSave">保存并发布简历</button></div></div>
<div id="form-image" class="hidden"><p class="muted">图片将存入仓库 <code>static/uploads/</code>，限制 4 MB；仅接受 PNG、JPG、WEBP、GIF、SVG。SVG 只建议上传可信来源文件。</p><div class="field"><label>选择图片</label><input id="imageFile" type="file" accept="image/png,image/jpeg,image/webp,image/gif,image/svg+xml"></div><button id="imageUpload">上传图片</button><div id="imageResult"></div></div>
<div id="form-browse" class="hidden"><button id="refreshList" class="secondary">刷新列表</button><div id="contentList" class="list"></div></div>
</section></main></div><script>
const $=id=>document.getElementById(id);let currentTab="post";
async function api(path,options={}){const r=await fetch("/api"+path,{credentials:"same-origin",...options,headers:{"content-type":"application/json",...(options.headers||{})}});const d=await r.json().catch(()=>({error:"服务器返回异常"}));if(!r.ok)throw Error(d.error||"请求失败");return d}
function status(s){$("status").textContent=s}
function showTab(tab){currentTab=tab;document.querySelectorAll("[data-tab]").forEach(b=>b.classList.toggle("active",b.dataset.tab===tab));["post","project","resume","image","browse"].forEach(t=>$("form-"+t).classList.toggle("hidden",t!==tab));$("heading").textContent=({post:"新增技术随笔",project:"新增项目",resume:"编辑简历资料",image:"上传图片",browse:"内容列表"})[tab];status("")}
document.querySelectorAll("[data-tab]").forEach(b=>b.onclick=()=>showTab(b.dataset.tab));
async function boot(){try{const me=await api("/me");if(me.authenticated){$("login").classList.add("hidden");$("app").classList.remove("hidden");$("user").textContent="@"+me.login;}}catch(e){status(e.message)}}
$("loginBtn").onclick=()=>location.href="/auth/login";$("logout").onclick=async()=>{await api("/auth/logout",{method:"POST",body:"{}"});location.reload()};
$("postPreview").onclick=()=>{const body=$("postBody").value;$("preview").classList.remove("hidden");$("preview").textContent=body.slice(0,4000);status("纯文本预览（未执行 HTML）。正式效果以 Hugo 页面为准。")};
$("postSave").onclick=async()=>{try{const title=$("postTitle").value.trim();if(!title)throw Error("请填写文章标题");const tags=$("postTags").value.split(/[,，]/).map(s=>s.trim()).filter(Boolean);const slug=$("postSlug").value.trim()||title;const body="---\ntitle: "+JSON.stringify(title)+"\ndate: "+new Date().toISOString()+"\nsummary: "+JSON.stringify($("postSummary").value.trim())+"\ntags: "+JSON.stringify(tags)+"\ndraft: false\n---\n\n"+$("postBody").value;const d=await api("/content/save",{method:"POST",body:JSON.stringify({kind:"post",slug,content:body})});status("已提交到 GitHub： "+d.path+"。Cloudflare Pages 完成构建后上线。")}catch(e){status(e.message)}};
$("projectSave").onclick=async()=>{try{const title=$("projectTitle").value.trim();if(!title)throw Error("请填写项目名称");const tags=$("projectTags").value.split(/[,，]/).map(s=>s.trim()).filter(Boolean);const body="---\ntitle: "+JSON.stringify(title)+"\ndate: "+new Date().toISOString()+"\nsummary: "+JSON.stringify($("projectSummary").value.trim())+"\ncategories: [\"项目实践\"]\ngithub: "+JSON.stringify($("projectRepo").value.trim())+"\ndemo: "+JSON.stringify($("projectDemo").value.trim())+"\ntech: "+JSON.stringify(tags)+"\nfeatured: false\nweight: 100\ndraft: false\n---\n\n"+$("projectBody").value;const d=await api("/content/save",{method:"POST",body:JSON.stringify({kind:"project",slug:$("projectSlug").value.trim()||title,content:body})});status("已提交到 GitHub："+d.path+"。请在项目页确认字段显示效果。")}catch(e){status(e.message)}};
$("resumeLoad").onclick=async()=>{try{const d=await api("/content/read?path="+encodeURIComponent("content/resume/_index.md"));$("resumeBody").value=d.content;status("已读取当前简历。")}catch(e){status(e.message)}};
$("resumeSave").onclick=async()=>{try{const content=$("resumeBody").value;if(!content.startsWith("---"))throw Error("简历内容必须保留以 --- 开头的 front matter");const d=await api("/content/save",{method:"POST",body:JSON.stringify({kind:"resume",content})});status("简历已提交："+d.path)}catch(e){status(e.message)}};
$("imageUpload").onclick=async()=>{try{const f=$("imageFile").files[0];if(!f)throw Error("请先选择图片");if(f.size>4*1024*1024)throw Error("图片不能超过 4 MB");const allowed=["image/png","image/jpeg","image/webp","image/gif","image/svg+xml"];if(!allowed.includes(f.type))throw Error("不支持该图片格式");const b64=await new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result).split(",")[1]);r.onerror=reject;r.readAsDataURL(f)});const d=await api("/upload",{method:"POST",body:JSON.stringify({name:f.name,type:f.type,data:b64})});$("imageResult").innerHTML="";const p=document.createElement("p");p.textContent="上传成功："+d.url;const input=document.createElement("input");input.value="!["+f.name+"]("+d.url+")";input.readOnly=true;input.onclick=()=>input.select();$("imageResult").append(p,input);status("图片已提交到仓库。")}catch(e){status(e.message)}};
$("refreshList").onclick=async()=>{try{const d=await api("/content/list");const root=$("contentList");root.replaceChildren();for(const item of d.items){const row=document.createElement("div");row.className="item";const name=document.createElement("span");name.textContent=item.type+" · "+item.title;const edit=document.createElement("button");edit.className="secondary";edit.textContent="读取";edit.onclick=async()=>{try{const v=await api("/content/read?path="+encodeURIComponent(item.path));if(item.type==="post"){showTab("post");$("postBody").value=v.content;status("已读取原始 Markdown；编辑 front matter 时请谨慎。")}else{showTab("project");$("projectBody").value=v.content;status("已读取原始项目 Markdown。")}}catch(e){status(e.message)}};row.append(name,edit);root.append(row)}}catch(e){status(e.message)}};
boot();
</script></body></html>`;

async function route(request, env) {
  const url = new URL(request.url);
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: { "access-control-allow-origin": env.ADMIN_ORIGIN, "access-control-allow-methods": "GET,POST,OPTIONS", "access-control-allow-headers": "content-type", "vary": "Origin" } });
  if (url.pathname === "/" || url.pathname === "/admin") return html(PAGE);
  if (url.pathname.startsWith("/api/") && !validOrigin(request, env)) return json({ error: "Origin 不允许" }, 403);
  if (url.pathname.startsWith("/api/") && request.method === "POST" && request.headers.get("content-type")?.split(";")[0].trim() !== "application/json") return json({ error: "仅接受 application/json 请求" }, 415);
  if (url.pathname === "/auth/login") {
    if (!env.GITHUB_CLIENT_ID || !env.SESSION_SECRET) return json({ error: "尚未配置 GITHUB_CLIENT_ID / SESSION_SECRET" }, 503);
    const state = randomHex(24);
    const target = new URL("https://github.com/login/oauth/authorize");
    target.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
    target.searchParams.set("redirect_uri", new URL("/auth/callback", request.url).toString());
    target.searchParams.set("scope", "repo read:user");
    target.searchParams.set("state", state);
    const headers = new Headers({ location: target.toString(), "cache-control": "no-store" });
    headers.append("set-cookie", cookie("bx_oauth_state", state, 600));
    return new Response(null, { status: 302, headers });
  }
  if (url.pathname === "/auth/callback") {
    const got = url.searchParams.get("state") || "";
    const expected = parseCookies(request).bx_oauth_state || "";
    if (!got || !(await safeEqual(got, expected))) return html("<h1>登录失败：OAuth state 校验未通过。</h1>", 400);
    const code = url.searchParams.get("code");
    if (!code) return html("<h1>GitHub 未返回授权码。</h1>", 400);
    const tokenRes = await fetch("https://github.com/login/oauth/access_token", { method:"POST", headers:{"accept":"application/json","content-type":"application/json"}, body:JSON.stringify({client_id:env.GITHUB_CLIENT_ID,client_secret:env.GITHUB_CLIENT_SECRET,code}) });
    const tokenData = await tokenRes.json();
    if (!tokenRes.ok || !tokenData.access_token) return html("<h1>GitHub 授权失败，请重试。</h1>", 401);
    const profile = await fetch("https://api.github.com/user", {headers:{authorization:"Bearer "+tokenData.access_token,accept:"application/vnd.github+json","user-agent":"Banxia-Content-Admin"}});
    const user = await profile.json();
    if (!profile.ok || user.login !== env.ALLOWED_GITHUB_LOGIN) return html("<h1>此 GitHub 账号未获准访问。</h1>", 403);
    const sessionCookie = await sealSession({token:tokenData.access_token,login:user.login,expires:Date.now()+SESSION_TTL},env.SESSION_SECRET);
    const headers = new Headers({location:"/","cache-control":"no-store"});
    headers.append("set-cookie", cookie(COOKIE,sessionCookie,SESSION_TTL));
    headers.append("set-cookie", cookie("bx_oauth_state","",0));
    return new Response(null,{status:302,headers});
  }
  if (url.pathname.startsWith("/api/")) {
    if (url.pathname === "/api/me" && request.method === "GET") {
      const s=await sessionFor(request,env); return json(s?{authenticated:true,login:s.login}:{authenticated:false});
    }
    if (url.pathname === "/api/auth/logout" && request.method === "POST") {
      return json({ok:true},200,{"set-cookie":cookie(COOKIE,"",0)});
    }
    const session = await sessionFor(request,env);
    if (!session) return json({error:"请先使用 GitHub 登录"},401);
    try {
      if (url.pathname === "/api/content/list" && request.method === "GET") return json({items:await listContent(env,session.token)});
      if (url.pathname === "/api/content/read" && request.method === "GET") {
        const path=url.searchParams.get("path")||"";
        const allowedContentPath = /^content\/(posts|projects)\/[\p{L}\p{N}_-]+(?:\/[\p{L}\p{N}_.-]+)*\.md$/u.test(path);
        if(!allowedContentPath && path!=="content/resume/_index.md") return json({error:"不允许读取此路径"},400);
        const file=await github(env,session.token,`/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path.split("/").map(encodeURIComponent).join("/")}?ref=${encodeURIComponent(env.GITHUB_BRANCH||"main")}`);
        return json({path,content:decodeURIComponent(escape(atob(file.content.replace(/\n/g,"")))),sha:file.sha});
      }
      if (url.pathname === "/api/content/save" && request.method === "POST") {
        const body=await request.json(); if(typeof body.content!=="string"||body.content.length>MAX_TEXT) return json({error:"内容为空或超过大小限制"},400);
        const path=safePath(body.kind,body.slug||"resume");
        if(body.kind==="post"&&!body.content.startsWith("---")) return json({error:"文章必须包含 Hugo front matter"},400);
        if(body.kind==="project"&&!body.content.startsWith("---")) return json({error:"项目必须包含 Hugo front matter"},400);
        if(body.kind==="resume"&& !body.content.startsWith("---")) return json({error:"简历必须保留 front matter"},400);
        let sha; try{const old=await github(env,session.token,`/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}?ref=${encodeURIComponent(env.GITHUB_BRANCH||"main")}`);sha=old.sha}catch(e){if(!String(e.message).includes("Not Found"))throw e;}
        const result=await putFile(env,session.token,path,body.content,`content-admin: update ${path}`,sha);
        return json({ok:true,path,commit:result.commit.html_url});
      }
      if (url.pathname === "/api/upload" && request.method === "POST") {
        const body=await request.json(); if(typeof body.data!=="string"||body.data.length>Math.ceil(MAX_IMAGE*4/3)+20) return json({error:"图片超过 4 MB"},400);
        const path=safePath("image","upload",body.name);
        const bytes=Uint8Array.from(atob(body.data),c=>c.charCodeAt(0));
        if(bytes.length>MAX_IMAGE) return json({error:"图片超过 4 MB"},400);
        const magic = body.type==="image/png" ? bytes[0]===137&&bytes[1]===80 : body.type==="image/jpeg" ? bytes[0]===255&&bytes[1]===216 : body.type==="image/gif" ? bytes[0]===71&&bytes[1]===73&&bytes[2]===70 : body.type==="image/webp" ? String.fromCharCode(...bytes.slice(8,12))==="WEBP" : body.type==="image/svg+xml" ? new TextDecoder().decode(bytes.slice(0,300)).includes("<svg") : false;
        if(!magic) return json({error:"文件内容与图片类型不匹配"},400);
        let sha;try{const old=await github(env,session.token,`/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}?ref=${encodeURIComponent(env.GITHUB_BRANCH||"main")}`);sha=old.sha}catch(e){if(!String(e.message).includes("Not Found"))throw e;}
        const result=await putFile(env,session.token,path,body.data,`content-admin: upload ${body.name}`,sha,true);
        return json({ok:true,path,url:env.SITE_URL+"/uploads/"+encodeURIComponent(body.name),commit:result.commit.html_url});
      }
      return json({error:"接口不存在"},404);
    } catch(e) { return json({error:e.message||"操作失败"},400); }
  }
  return new Response("Not found",{status:404});
}
export default { async fetch(request,env) { try { return await route(request,env); } catch(e) { return json({error:"服务器内部错误",detail:env.ENVIRONMENT==="development"?e.message:undefined},500); } } };
