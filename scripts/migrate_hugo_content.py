#!/usr/bin/env python3
"""Export Hugo Page Bundles to Vue's public content catalogue without deleting sources."""
from __future__ import annotations

import json
import re
import shutil
import tomllib
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PUBLIC = ROOT / "frontend" / "public" / "content"
OUT = PUBLIC / "catalog.json"


def parse_page(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("+++"):
        _, meta, body = raw.split("+++", 2)
        return tomllib.loads(meta), body.lstrip()
    if raw.startswith("---"):
        _, meta, body = raw.split("---", 2)
        return (yaml.safe_load(meta) or {}), body.lstrip()
    return {}, raw


def json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_value(v) for v in value]
    return value


def as_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    return value if isinstance(value, list) else [value]


def rewrite_assets(markdown: str, collection: str, bundle_slug: str) -> str:
    prefix = f"/content/{collection}/{bundle_slug}/"
    markdown = re.sub(
        r'(!\[[^\]]*\]\()((?!https?://|/)[^\)]+)(\))',
        lambda m: m.group(1) + prefix + m.group(2) + m.group(3), markdown,
    )
    markdown = re.sub(
        r'(<img[^>]+src=["\'])((?!https?://|/)[^"\']+)(["\'])',
        lambda m: m.group(1) + prefix + m.group(2) + m.group(3),
        markdown, flags=re.IGNORECASE,
    )
    return markdown


def copy_bundle_assets(page: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for asset in page.parent.iterdir():
        if asset.is_file() and asset.name.lower() != "index.md":
            shutil.copy2(asset, target / asset.name)
        elif asset.is_dir() and asset.name != ".git":
            destination = target / asset.name
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(asset, destination)


def migrate_collection(name: str, warnings: list[str]) -> list[dict[str, Any]]:
    source = CONTENT / name
    result: list[dict[str, Any]] = []
    if not source.exists():
        return result

    for page in sorted(source.rglob("index.md")):
        relative = page.relative_to(source)
        if any(part.startswith("_") for part in relative.parts):
            continue

        bundle_slug = page.parent.name if page.parent != source else name
        meta, body = parse_page(page)
        if meta.get("draft") is True:
            continue

        copy_bundle_assets(page, PUBLIC / name / bundle_slug)
        slug = str(meta.get("slug") or bundle_slug)
        title = str(meta.get("title") or slug)
        date_value = json_value(meta.get("date") or meta.get("publishDate") or "")

        cover = meta.get("cover") or ""
        if isinstance(cover, dict):
            cover = cover.get("image") or cover.get("src") or ""
        if cover and not str(cover).startswith(("http://", "https://", "/")):
            cover = f"/content/{name}/{bundle_slug}/{cover}"

        tags = as_list(meta.get("tags"))
        tech = as_list(meta.get("tech"))
        categories = as_list(meta.get("categories"))
        # Project cards use tags for their technology labels; preserve the original tech field too.
        display_tags = tags or tech

        route_value = str(meta.get("url") or meta.get("permalink") or f"/{name}/{slug}/")
        if route_value.startswith(("http://", "https://")):
            route_value = urlsplit(route_value).path or f"/{name}/{slug}/"
        if not route_value.startswith("/"):
            route_value = "/" + route_value

        if "{{<" in body or "{{%" in body:
            warnings.append(f"{page.relative_to(ROOT)}: contains Hugo shortcode syntax; manual conversion required")
        if re.search(r'!?\[[^\]]*\]\((?!https?://|/)[^)]*\)', body):
            warnings.append(f"{page.relative_to(ROOT)}: contains relative Markdown links; verify exported asset paths")

        result.append({
            "slug": slug,
            "category": "project" if name == "projects" else "post",
            "title": title,
            "summary": str(meta.get("summary") or meta.get("description") or ""),
            "date": date_value,
            "tags": display_tags,
            "tech": tech,
            "categories": categories,
            "github": str(meta.get("github") or ""),
            "draft": bool(meta.get("draft", False)),
            "weight": meta.get("weight", 0),
            "featured": bool(meta.get("featured", False)),
            "cover": str(cover),
            "content": rewrite_assets(body, name, bundle_slug),
            "permalink": route_value,
            "href": route_value,
            "source": page.relative_to(ROOT).as_posix(),
        })
    return result


def migrate_resume(warnings: list[str]) -> list[dict[str, Any]]:
    resume_dir = CONTENT / "resume"
    result: list[dict[str, Any]] = []
    if not resume_dir.exists():
        return result
    pages = sorted(set(resume_dir.rglob("index.md")) | set(resume_dir.rglob("_index.md")))
    for page in pages:
        meta, body = parse_page(page)
        if "{{<" in body or "{{%" in body:
            warnings.append(f"{page.relative_to(ROOT)}: contains Hugo shortcode syntax; manual conversion required")
        result.append({
            "meta": json_value(meta),
            "content": body,
            "source": page.relative_to(ROOT).as_posix(),
        })
    return result


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    static_dir = ROOT / "static"
    if static_dir.exists():
        shutil.copytree(static_dir, ROOT / "frontend" / "public", dirs_exist_ok=True)

    warnings: list[str] = []
    posts = migrate_collection("posts", warnings)
    projects = migrate_collection("projects", warnings)
    payload = {
        "generatedAt": datetime.now().astimezone().isoformat(),
        "posts": posts,
        "projects": projects,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    resume = migrate_resume(warnings)
    (PUBLIC / "resume.json").write_text(
        json.dumps(resume, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"迁移完成：{len(posts)} 篇随笔，{len(projects)} 个项目，{len(resume)} 份简历内容")
    print(f"目录文件：{OUT.relative_to(ROOT)}")
    if warnings:
        print("需要人工核查的项目：")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("未检测到 Hugo Shortcodes 或相对 Markdown 链接；仍需浏览器抽查页面和资源。")
    print("原始 Hugo content 未修改。")


if __name__ == "__main__":
    main()
