# 半夏小筑

基于 Hugo + PaperMod 构建的个人网站。

线上地址：https://www.banxia.xin/

## 本地预览

先安装与项目兼容的 Hugo 版本，并确保 PaperMod 主题已就位。

```bash
hugo server -D
```

浏览器打开终端提示的本地地址。此命令会显示草稿内容，适合写作和检查。

## 新增一篇随笔

使用短横线分隔英文 slug，避免把标题直接当作目录名：

```bash
hugo new content posts/opencv-basics/index.md
```

Hugo 会优先使用 `archetypes/posts/index.md` 模板。然后编辑生成的 `content/posts/opencv-basics/index.md`。

## 新增一个项目

```bash
hugo new content projects/industrial-vision/index.md
```

Hugo 会使用 `archetypes/projects/index.md` 模板。项目目录可以独立存放封面和截图，例如：

```text
content/projects/industrial-vision/
├── index.md
├── cover.png
└── screenshots/
    ├── main.png
    └── result.png
```

图片放入对应项目目录后，可在 Markdown 中用相对路径引用：

```markdown
![程序主界面](screenshots/main.png)
```

若要在 PaperMod 文章页显示封面，请按主题支持的 `cover` 参数配置图片；项目列表是否展示封面还取决于站点当前的项目列表模板。

## 常用 Front Matter 字段

### 随笔

- `title`：文章标题
- `date`：创建日期
- `summary`：列表页摘要
- `tags`：标签数组
- `categories`：分类数组
- `draft`：是否为草稿；确认发布前改为 `false`

### 项目

除上述通用字段外，项目模板还预留：

- `github`：源码仓库地址
- `demo`：在线演示地址（没有可留空）
- `tech`：技术栈数组
- `featured`：是否作为精选项目
- `weight`：列表排序权重

这些字段先作为内容元数据；若页面布局尚未读取某个字段，它不会自动变成可见内容，需要在模板中接入后才会显示。

## 构建检查

```bash
hugo --gc --minify
```

构建成功后再提交和推送 Git。正式部署仍以仓库当前配置的托管平台和工作流为准；不要在未确认部署方式前手动删除或忽略 `public/`。

## 内容组织约定

新内容使用 Page Bundle：

- 随笔：`content/posts/<slug>/index.md`
- 项目：`content/projects/<slug>/index.md`

每个内容目录可以携带自己的图片和其他资源。已有文章会在后续迁移阶段逐一处理，迁移时需检查旧 URL，避免收藏链接失效。
