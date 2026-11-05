#!/usr/bin/env python3
"""Convert Hugo Page Bundles to Vue's static content catalogue without deleting source files."""
from __future__ import annotations

import json
import re
import shutil
import tomllib
from datetime import date, datetime
from pathlib import Path
from typing import Any

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


def rewrite_assets(markdown: str, collection: str, slug: str) -> str:
    prefix = f"/content/{collection}/{slug}/"
    # Hugo Page Bundle relative image/file links become stable public asset paths.
    markdown = re.sub(r'(!\[[^\]]*\]\()((?!https?://|/)[^\)]+)(\))',
                      lambda m: m.group(1) + prefix + m.group(2) + m.group(3), markdown)
    markdown = re.sub(r'(<img[^>]+src=["\'])((?!https?://|/)[^"\']+)(["\'])',
                      lambda m: m.group(1) + prefix + m.group(2) + m.group(3), markdown,
                      flags=re.IGNORECASE)
    return markdown


def migrate_collection(name: str) -> list[dict[str, Any]]:
    source = CONTENT / name
    result: list[dict[str, Any]] = []
    if not source.exists():
        return result
    for page in sorted(source.rglob("index.md")):
        if any(part.startswith("_") for part in page.relative_to(source).parts):
            continue
        slug = page.parent.name
        if page.parent == source:
            slug = name
        meta, body = parse_page(page)
        if meta.get("draft") is True:
            continue
        asset_target = PUBLIC / name / slug
        asset_target.mkdir(parents=True, exist_ok=True)
        for asset in page.parent.iterdir():
            if asset.is_file() and asset.name.lower() != "index.md":
                shutil.copy2(asset, asset_target / asset.name)
            elif asset.is_dir() and asset.name not in {".git"}:
                target = asset_target / asset.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(asset, target)
        title = str(meta.get("title") or slug)
        date_value = json_value(meta.get("date") or meta.get("publishDate") or "")
        cover = meta.get("cover") or {}
        if isinstance(cover, dict):
            cover = cover.get("image") or cover.get("src") or ""
        if cover and not str(cover).startswith(("http://", "https://", "/")):
            cover = f"/content/{name}/{slug}/{cover}"
        result.append({
            "slug": slug,
            "title": title,
            "summary": str(meta.get("summary") or meta.get("description") or ""),
            "date": date_value,
            "tags": meta.get("tags") or [],
            "categories": meta.get("categories") or [],
            "draft": bool(meta.get("draft", False)),
            "weight": meta.get("weight", 0),
            "featured": bool(meta.get("featured", False)),
            "cover": cover,
            "content": rewrite_assets(body, name, slug),
            "permalink": f"/{name}/{slug}/",
            "source": page.relative_to(ROOT).as_posix(),
        })
    return result


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now().astimezone().isoformat(),
        "posts": migrate_collection("posts"),
        "projects": migrate_collection("projects"),
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    resume_dir = CONTENT / "resume"
    resume = []
    if resume_dir.exists():
        for page in resume_dir.rglob("index.md"):
            meta, body = parse_page(page)
            resume.append({"meta": json_value(meta), "content": body})
    (PUBLIC / "resume.json").write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"迁移完成：{len(payload['posts'])} 篇随笔，{len(payload['projects'])} 个项目")
    print(f"目录文件：{OUT.relative_to(ROOT)}")
    print("原始 Hugo content 未修改；请人工核对图片引用、Shortcodes 和特殊 front matter。")


if __name__ == "__main__":
    main()
