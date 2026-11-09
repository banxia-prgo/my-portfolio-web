#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_ID="${1:-}"

# 只接受 GitHub Actions 生成的部署编号
if [[ ! "$DEPLOY_ID" =~ ^[0-9]+-[0-9]+-[a-f0-9]{40}$ ]]; then
    echo "ERROR: invalid deployment ID"
    exit 1
fi

LIVE_DIR="/var/www/banxia-frontend"
INCOMING_DIR="/home/deploy/incoming"
STAGING_DIR="/home/deploy/staging/${DEPLOY_ID}"
BACKUP_DIR="/home/deploy/backups/${DEPLOY_ID}"
ARCHIVE="${INCOMING_DIR}/frontend-${DEPLOY_ID}.tar.gz"

DEPLOY_STARTED=0

rollback() {
    status=$?
    trap - EXIT

    if [[ "$status" -ne 0 && "$DEPLOY_STARTED" -eq 1 ]]; then
        echo "ERROR: deployment failed; restoring previous website"

        if [[ -d "$BACKUP_DIR" ]]; then
            rsync -a --delete "$BACKUP_DIR/" "$LIVE_DIR/"
            echo "Rollback completed"
        else
            echo "ERROR: backup directory not found"
        fi
    fi

    exit "$status"
}

trap rollback EXIT

# 基础检查
test -d "$LIVE_DIR"
test -s "$ARCHIVE"
tar -tzf "$ARCHIVE" >/dev/null

if [[ -e "$BACKUP_DIR" ]]; then
    echo "ERROR: backup already exists"
    exit 1
fi

mkdir -p "$STAGING_DIR" "$BACKUP_DIR"

# 解压新版本
tar -xzf "$ARCHIVE" -C "$STAGING_DIR"

if [[ ! -s "$STAGING_DIR/index.html" ]]; then
    echo "ERROR: index.html missing from build"
    exit 1
fi

# 备份当前网站
echo "Creating website backup..."
rsync -a --delete "$LIVE_DIR/" "$BACKUP_DIR/"

# 开始更新
DEPLOY_STARTED=1

echo "Updating website files..."

# 保留 .well-known，避免影响 ACME 证书验证
rsync -a --delete \
    --exclude='/.well-known/' \
    "$STAGING_DIR/" "$LIVE_DIR/"

# 确保 Nginx 可以读取新文件
chgrp -R www-data "$LIVE_DIR"
find "$LIVE_DIR" -type d -exec chmod 755 {} \;
find "$LIVE_DIR" -type f -exec chmod 644 {} \;

# 检查 Nginx 是否正常返回网站
echo "Checking website response..."
curl --fail --silent --show-error \
    --max-time 10 \
    http://127.0.0.1/ \
    -o /dev/null

echo "Website deployment successful"

DEPLOY_STARTED=0

# 清理临时文件
rm -rf -- "$STAGING_DIR"
rm -f -- "$ARCHIVE"

# 保留最近 5 次备份
find /home/deploy/backups \
    -mindepth 1 -maxdepth 1 -type d \
    -printf '%T@ %p\n' |
    sort -nr |
    awk 'NR > 5 {sub(/^[^ ]+ /, ""); print}' |
    while IFS= read -r old_backup; do
        rm -rf -- "$old_backup"
    done

echo "Deployment ID: $DEPLOY_ID"
echo "Backup retained: $BACKUP_DIR"