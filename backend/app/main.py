from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import User, UserSession, Comment, ArticleLike, ArticleBookmark
from .schemas import RegisterIn, LoginIn, UserOut, CommentIn
from .security import hash_password, verify_password, new_session_token, token_digest, session_expiry, new_csrf_token
from .settings import settings
from .rate_limit import limit_attempts

app = FastAPI(title="半夏小筑 API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["GET","POST","DELETE","OPTIONS"], allow_headers=["Content-Type","X-CSRF-Token"])

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
    response.set_cookie(CSRF_COOKIE, token, httponly=True, secure=settings.cookie_secure, samesite="lax", path="/", max_age=3600)
    return {"csrf_token": token}

@app.post("/api/auth/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, request: Request, response: Response, db: Session = Depends(get_db)):
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
def login(data: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
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
