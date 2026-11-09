from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import User, UserSession, Comment, ArticleLike, ArticleBookmark, GuestbookMessage, AuditLog, ContentItem, ContentCategory, ContentTag, MediaAsset, SiteSetting
from .schemas import RegisterIn, LoginIn, UserOut, CommentIn, ProfileUpdate, GuestbookMessageIn, AdminUserUpdate, ContentCreate, ContentUpdate, TaxonomyCreate, SiteSettingUpdate
from .security import hash_password, verify_password, new_session_token, token_digest, session_expiry, new_csrf_token
from .settings import settings
from .rate_limit import limit_attempts

app = FastAPI(title="半夏小筑 API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"], allow_headers=["Content-Type","X-CSRF-Token"])

SESSION_COOKIE = "bx_session"
CSRF_COOKIE = "bx_csrf"

@app.get("/")
def root():
    return {"name":"半夏小筑 API","version":"1.0.0"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status":"ok","database":"connected"}

def current_user(request: Request, db: Session) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    session = db.scalar(select(UserSession).where(UserSession.token_hash == token_digest(token)))
    if not session or session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="登录已过期")
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="账号不可用")
    return user

def require_csrf(request: Request, header: str | None):
    cookie = request.cookies.get(CSRF_COOKIE)
    if not cookie or not header or not secrets_compare(cookie, header):
        raise HTTPException(status_code=403, detail="CSRF 校验失败")

def secrets_compare(a: str, b: str) -> bool:
    import hmac
    return hmac.compare_digest(a, b)

def set_auth_cookies(response: Response, token: str):
    max_age = settings.session_ttl_hours * 3600
    common = {"secure": settings.cookie_secure, "samesite":"lax", "path":"/", "max_age":max_age}
    response.set_cookie(SESSION_COOKIE, token, httponly=True, **common)

@app.get("/api/auth/csrf")
def issue_csrf_token(response: Response):
    token = new_csrf_token()
    response.set_cookie(CSRF_COOKIE, token, httponly=True, secure=settings.cookie_secure, samesite="lax", path="/", max_age=settings.session_ttl_hours * 3600)
    return {"csrf_token": token}

@app.post("/api/auth/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, request: Request, response: Response, x_csrf_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    require_csrf(request, x_csrf_token)
    limit_attempts(request, key="register", maximum=5, window_seconds=3600)
    email = str(data.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="该邮箱已注册")
    user = User(email=email, nickname=data.nickname.strip(), password_hash=hash_password(data.password))
    db.add(user); db.flush()
    token = new_session_token()
    db.add(UserSession(user_id=user.id, token_hash=token_digest(token), expires_at=session_expiry()))
    db.commit(); db.refresh(user)
    set_auth_cookies(response, token)
    return user

@app.post("/api/auth/login", response_model=UserOut)
def login(data: LoginIn, request: Request, response: Response, x_csrf_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    require_csrf(request, x_csrf_token)
    limit_attempts(request, key="login", maximum=10, window_seconds=900)
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = new_session_token()
    db.add(UserSession(user_id=user.id, token_hash=token_digest(token), expires_at=session_expiry()))
    db.commit(); set_auth_cookies(response, token)
    return user

@app.post("/api/auth/logout")
def logout(request: Request, response: Response, x_csrf_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    require_csrf(request, x_csrf_token)
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = db.scalar(select(UserSession).where(UserSession.token_hash == token_digest(token)))
        if session: db.delete(session); db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")
    return {"ok":True}

@app.get("/api/users/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    return current_user(request, db)

@app.patch("/api/users/me", response_model=UserOut)
def update_profile(data: ProfileUpdate, request: Request, x_csrf_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    require_csrf(request, x_csrf_token)
    user = current_user(request, db)
    nickname = data.nickname.strip()
    if not nickname:
        raise HTTPException(status_code=422, detail="昵称不能为空")
    user.nickname = nickname
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/comments", status_code=201)
def create_comment(data: CommentIn, request: Request, x_csrf_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    require_csrf(request, x_csrf_token)
    user = current_user(request, db)
    if data.parent_id:
        parent = db.get(Comment, data.parent_id)
        if not parent or parent.article_slug != data.article_slug or parent.is_deleted:
            raise HTTPException(status_code=404, detail="回复目标不存在")
    item = Comment(article_slug=data.article_slug, user_id=user.id, parent_id=data.parent_id, content=data.content.strip())
    db.add(item); db.commit(); db.refresh(item)
    return {"id":item.id,"article_slug":item.article_slug,"content":item.content,"nickname":user.nickname,"parent_id":item.parent_id,"created_at":item.created_at}

@app.get("/api/articles/{slug}/comments")
def list_comments(slug: str, db: Session = Depends(get_db)):
    rows = db.execute(select(Comment, User).join(User).where(Comment.article_slug==slug, Comment.is_deleted.is_(False)).order_by(Comment.created_at.desc()).limit(100)).all()
    return [{"id":c.id,"content":c.content,"nickname":u.nickname,"parent_id":c.parent_id,"created_at":c.created_at} for c,u in rows]

def toggle_relation(model, slug: str, request: Request, x_csrf_token: str | None, db: Session):
    require_csrf(request, x_csrf_token)
    user = current_user(request, db)
    item = db.scalar(select(model).where(model.article_slug==slug, model.user_id==user.id))
    if item:
        db.delete(item); active=False
    else:
        db.add(model(article_slug=slug,user_id=user.id)); active=True
    db.commit()
    return {"active":active}

@app.post("/api/articles/{slug}/likes")
def toggle_like(slug: str, request: Request, x_csrf_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    return toggle_relation(ArticleLike, slug, request, x_csrf_token, db)

@app.post("/api/articles/{slug}/bookmarks")
def toggle_bookmark(slug: str, request: Request, x_csrf_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    return toggle_relation(ArticleBookmark, slug, request, x_csrf_token, db)

@app.get("/api/users/me/activity")
def activity(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    likes = db.scalars(select(ArticleLike.article_slug).where(ArticleLike.user_id==user.id)).all()
    bookmarks = db.scalars(select(ArticleBookmark.article_slug).where(ArticleBookmark.user_id==user.id)).all()
    comments = db.scalars(select(Comment).where(Comment.user_id==user.id, Comment.is_deleted.is_(False)).order_by(Comment.created_at.desc()).limit(100)).all()
    return {"likes":likes,"bookmarks":bookmarks,"comments":[{"id":c.id,"article_slug":c.article_slug,"content":c.content,"created_at":c.created_at} for c in comments]}


@app.get("/api/articles/{slug}/stats")
def article_stats(slug: str, request: Request, db: Session = Depends(get_db)):
    likes = db.scalar(select(func.count()).select_from(ArticleLike).where(ArticleLike.article_slug == slug)) or 0
    comments = db.scalar(select(func.count()).select_from(Comment).where(Comment.article_slug == slug, Comment.is_deleted.is_(False))) or 0
    bookmarks = db.scalar(select(func.count()).select_from(ArticleBookmark).where(ArticleBookmark.article_slug == slug)) or 0
    user_id = None
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = db.scalar(select(UserSession).where(UserSession.token_hash == token_digest(token)))
        if session and session.expires_at > datetime.now(timezone.utc):
            user_id = session.user_id
    liked = bool(user_id and db.scalar(select(ArticleLike.id).where(ArticleLike.article_slug == slug, ArticleLike.user_id == user_id)))
    bookmarked = bool(user_id and db.scalar(select(ArticleBookmark.id).where(ArticleBookmark.article_slug == slug, ArticleBookmark.user_id == user_id)))
    return {"likes": likes, "comments": comments, "bookmarks": bookmarks, "liked": liked, "bookmarked": bookmarked}


@app.get("/api/guestbook/messages")
def list_guestbook_messages(db: Session = Depends(get_db)):
    rows = db.execute(
        select(GuestbookMessage, User)
        .join(User)
        .where(GuestbookMessage.is_deleted.is_(False))
        .order_by(GuestbookMessage.created_at.desc())
        .limit(100)
    ).all()
    return [
        {
            "id": item.id,
            "content": item.content,
            "nickname": user.nickname,
            "created_at": item.created_at,
        }
        for item, user in rows
    ]


@app.post("/api/guestbook/messages", status_code=201)
def create_guestbook_message(
    data: GuestbookMessageIn,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    user = current_user(request, db)
    limit_attempts(request, key="guestbook", maximum=5, window_seconds=3600)
    content = data.content
    item = GuestbookMessage(user_id=user.id, content=content)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        "id": item.id,
        "content": item.content,
        "nickname": user.nickname,
        "created_at": item.created_at,
    }



def is_admin_user(user: User) -> bool:
    configured = {
        item.strip().lower()
        for item in settings.admin_emails.split(",")
        if item.strip()
    }
    return user.role == "admin" or user.email.lower() in configured


def require_admin(request: Request, db: Session) -> User:
    user = current_user(request, db)
    if not is_admin_user(user):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def write_audit_log(
    db: Session,
    actor: User,
    action: str,
    target_type: str,
    target_id: str | int | None = None,
    detail: str | None = None,
) -> None:
    db.add(AuditLog(
        actor_user_id=actor.id,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        detail=detail,
    ))


@app.get("/api/admin/me")
def admin_me(request: Request, db: Session = Depends(get_db)):
    user = require_admin(request, db)
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "role": "admin",
        "is_active": user.is_active,
    }


@app.get("/api/admin/overview")
def admin_overview(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    return {
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "active_users": db.scalar(select(func.count()).select_from(User).where(User.is_active.is_(True))) or 0,
        "comments": db.scalar(select(func.count()).select_from(Comment).where(Comment.is_deleted.is_(False))) or 0,
        "guestbook_messages": db.scalar(select(func.count()).select_from(GuestbookMessage).where(GuestbookMessage.is_deleted.is_(False))) or 0,
    }


@app.get("/api/admin/users")
def admin_list_users(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    total = db.scalar(select(func.count()).select_from(User)) or 0
    users = db.scalars(select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)).all()
    return {
        "items": [
            {
                "id": item.id,
                "email": item.email,
                "nickname": item.nickname,
                "avatar_url": item.avatar_url,
                "is_active": item.is_active,
                "role": "admin" if is_admin_user(item) else "user",
                "created_at": item.created_at,
            }
            for item in users
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.patch("/api/admin/users/{user_id}")
def admin_update_user(
    user_id: int,
    data: AdminUserUpdate,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = require_admin(request, db)
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.id == actor.id and (data.is_active is False or data.role == "user"):
        raise HTTPException(status_code=400, detail="不能停用或降级当前管理员账号")
    if data.is_active is not None:
        target.is_active = data.is_active
        if not data.is_active:
            sessions = db.scalars(select(UserSession).where(UserSession.user_id == target.id)).all()
            for session in sessions:
                db.delete(session)
    if data.role is not None:
        target.role = data.role
    write_audit_log(db, actor, "user.update", "user", target.id, f"is_active={data.is_active}; role={data.role}")
    db.commit()
    db.refresh(target)
    return {
        "id": target.id,
        "email": target.email,
        "nickname": target.nickname,
        "is_active": target.is_active,
        "role": "admin" if is_admin_user(target) else "user",
    }


@app.get("/api/admin/audit-logs")
def admin_audit_logs(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    rows = db.execute(
        select(AuditLog, User)
        .outerjoin(User, AuditLog.actor_user_id == User.id)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [
        {
            "id": log.id,
            "actor_user_id": log.actor_user_id,
            "actor_nickname": actor.nickname if actor else None,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "detail": log.detail,
            "created_at": log.created_at,
        }
        for log, actor in rows
    ]


@app.delete("/api/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = current_user(request, db)
    comment = db.get(Comment, comment_id)
    if not comment or comment.is_deleted:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.user_id != actor.id and not is_admin_user(actor):
        raise HTTPException(status_code=403, detail="无权删除这条评论")
    comment.is_deleted = True
    if is_admin_user(actor) and comment.user_id != actor.id:
        write_audit_log(db, actor, "comment.delete", "comment", comment.id)
    db.commit()
    return {"ok": True}


@app.delete("/api/guestbook/messages/{message_id}")
def delete_guestbook_message(
    message_id: int,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = current_user(request, db)
    message = db.get(GuestbookMessage, message_id)
    if not message or message.is_deleted:
        raise HTTPException(status_code=404, detail="留言不存在")
    if message.user_id != actor.id and not is_admin_user(actor):
        raise HTTPException(status_code=403, detail="无权删除这条留言")
    message.is_deleted = True
    if is_admin_user(actor) and message.user_id != actor.id:
        write_audit_log(db, actor, "guestbook.delete", "guestbook_message", message.id)
    db.commit()
    return {"ok": True}



def serialize_content(item: ContentItem) -> dict:
    return {
        "id": item.id,
        "kind": item.kind,
        "slug": item.slug,
        "title": item.title,
        "summary": item.summary,
        "content": item.content,
        "status": item.status,
        "featured": item.featured,
        "sort_order": item.sort_order,
        "cover_url": item.cover_url,
        "github_url": item.github_url,
        "categories": [{"id": c.id, "name": c.name, "slug": c.slug} for c in item.categories],
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in item.tags],
        "published_at": item.published_at,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def apply_taxonomy(db: Session, item: ContentItem, category_ids: list[int], tag_ids: list[int]) -> None:
    categories = db.scalars(select(ContentCategory).where(ContentCategory.id.in_(category_ids))).all() if category_ids else []
    tags = db.scalars(select(ContentTag).where(ContentTag.id.in_(tag_ids))).all() if tag_ids else []
    if len(categories) != len(set(category_ids)):
        raise HTTPException(status_code=422, detail="包含不存在的分类")
    if len(tags) != len(set(tag_ids)):
        raise HTTPException(status_code=422, detail="包含不存在的标签")
    item.categories = categories
    item.tags = tags


@app.get("/api/content/{kind}")
def public_content_list(kind: str, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    if kind not in {"posts", "projects"}:
        raise HTTPException(status_code=404, detail="内容类型不存在")
    content_kind = "post" if kind == "posts" else "project"
    rows = db.scalars(
        select(ContentItem)
        .where(ContentItem.kind == content_kind, ContentItem.status == "published")
        .order_by(ContentItem.featured.desc(), ContentItem.sort_order, ContentItem.published_at.desc())
        .offset(max(0, offset))
        .limit(max(1, min(limit, 100)))
    ).all()
    return [serialize_content(item) for item in rows]


@app.get("/api/content/{kind}/{slug}")
def public_content_detail(kind: str, slug: str, db: Session = Depends(get_db)):
    if kind not in {"posts", "projects"}:
        raise HTTPException(status_code=404, detail="内容类型不存在")
    content_kind = "post" if kind == "posts" else "project"
    item = db.scalar(select(ContentItem).where(
        ContentItem.kind == content_kind,
        ContentItem.slug == slug,
        ContentItem.status == "published",
    ))
    if not item:
        raise HTTPException(status_code=404, detail="内容不存在")
    return serialize_content(item)


@app.get("/api/site/profile")
def public_site_profile(db: Session = Depends(get_db)):
    setting = db.get(SiteSetting, "profile")
    return setting.value if setting else {}


@app.get("/api/admin/content")
def admin_content_list(
    request: Request,
    kind: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    query = select(ContentItem)
    if kind in {"post", "project"}:
        query = query.where(ContentItem.kind == kind)
    if status in {"draft", "published", "archived"}:
        query = query.where(ContentItem.status == status)
    query = query.order_by(ContentItem.updated_at.desc()).offset(max(0, offset)).limit(max(1, min(limit, 100)))
    return [serialize_content(item) for item in db.scalars(query).all()]


@app.post("/api/admin/content", status_code=201)
def admin_create_content(
    data: ContentCreate,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = require_admin(request, db)
    if db.scalar(select(ContentItem.id).where(ContentItem.kind == data.kind, ContentItem.slug == data.slug)):
        raise HTTPException(status_code=409, detail="该内容标识已存在")
    now = datetime.now(timezone.utc)
    item = ContentItem(
        kind=data.kind, slug=data.slug, title=data.title, summary=data.summary,
        content=data.content, status=data.status, featured=data.featured,
        sort_order=data.sort_order, cover_url=data.cover_url, github_url=data.github_url,
        created_by=actor.id, updated_by=actor.id,
        published_at=now if data.status == "published" else None,
    )
    apply_taxonomy(db, item, data.category_ids, data.tag_ids)
    db.add(item)
    db.flush()
    write_audit_log(db, actor, "content.create", data.kind, item.id, data.slug)
    db.commit()
    db.refresh(item)
    return serialize_content(item)


@app.patch("/api/admin/content/{content_id}")
def admin_update_content(
    content_id: int,
    data: ContentUpdate,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = require_admin(request, db)
    item = db.get(ContentItem, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="内容不存在")
    values = data.model_dump(exclude_unset=True)
    category_ids = values.pop("category_ids", None)
    tag_ids = values.pop("tag_ids", None)
    next_slug = values.get("slug", item.slug)
    if db.scalar(select(ContentItem.id).where(
        ContentItem.kind == item.kind, ContentItem.slug == next_slug, ContentItem.id != item.id
    )):
        raise HTTPException(status_code=409, detail="该内容标识已存在")
    for key, value in values.items():
        setattr(item, key, value)
    if category_ids is not None or tag_ids is not None:
        apply_taxonomy(
            db, item,
            category_ids if category_ids is not None else [c.id for c in item.categories],
            tag_ids if tag_ids is not None else [t.id for t in item.tags],
        )
    if item.status == "published" and item.published_at is None:
        item.published_at = datetime.now(timezone.utc)
    item.updated_by = actor.id
    write_audit_log(db, actor, "content.update", item.kind, item.id, item.slug)
    db.commit()
    db.refresh(item)
    return serialize_content(item)


@app.delete("/api/admin/content/{content_id}")
def admin_delete_content(
    content_id: int,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = require_admin(request, db)
    item = db.get(ContentItem, content_id)
    if not item:
        raise HTTPException(status_code=404, detail="内容不存在")
    write_audit_log(db, actor, "content.delete", item.kind, item.id, item.slug)
    db.delete(item)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/categories")
def admin_categories(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    return db.scalars(select(ContentCategory).order_by(ContentCategory.name)).all()


@app.post("/api/admin/categories", status_code=201)
def admin_create_category(
    data: TaxonomyCreate,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = require_admin(request, db)
    item = ContentCategory(name=data.name.strip(), slug=data.slug.strip(), description=data.description)
    db.add(item)
    write_audit_log(db, actor, "category.create", "category", data.slug)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "slug": item.slug, "description": item.description}


@app.get("/api/admin/tags")
def admin_tags(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    return db.scalars(select(ContentTag).order_by(ContentTag.name)).all()


@app.post("/api/admin/tags", status_code=201)
def admin_create_tag(
    data: TaxonomyCreate,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = require_admin(request, db)
    item = ContentTag(name=data.name.strip(), slug=data.slug.strip())
    db.add(item)
    write_audit_log(db, actor, "tag.create", "tag", data.slug)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "slug": item.slug}


@app.put("/api/admin/site-settings/{key}")
def admin_update_site_setting(
    key: str,
    data: SiteSettingUpdate,
    request: Request,
    x_csrf_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_csrf(request, x_csrf_token)
    actor = require_admin(request, db)
    if key not in {"profile", "homepage", "seo", "contact", "announcement"}:
        raise HTTPException(status_code=400, detail="不支持的配置项")
    setting = db.get(SiteSetting, key)
    if not setting:
        setting = SiteSetting(key=key, value=data.value, updated_by=actor.id)
        db.add(setting)
    else:
        setting.value = data.value
        setting.updated_by = actor.id
    write_audit_log(db, actor, "site_setting.update", "site_setting", key)
    db.commit()
    return {"key": key, "value": setting.value}


@app.get("/api/admin/media")
def admin_media_list(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    items = db.scalars(
        select(MediaAsset).order_by(MediaAsset.created_at.desc())
        .offset(max(0, offset)).limit(max(1, min(limit, 100)))
    ).all()
    return [
        {
            "id": item.id, "original_name": item.original_name,
            "public_url": item.public_url, "mime_type": item.mime_type,
            "size_bytes": item.size_bytes, "alt_text": item.alt_text,
            "created_at": item.created_at,
        }
        for item in items
    ]
