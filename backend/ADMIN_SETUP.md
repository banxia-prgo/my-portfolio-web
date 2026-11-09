# Backend administrator bootstrap

The first administrator is granted through a server-side environment variable. Do not expose this value in frontend build variables or commit it to the repository.

## Configure

Set `ADMIN_EMAILS` in the backend container environment to the email address of an account that has already registered on the site.

Example (replace with the actual account email):

```env
ADMIN_EMAILS=your-admin@example.com
```

Multiple administrator addresses can be comma-separated:

```env
ADMIN_EMAILS=admin1@example.com,admin2@example.com
```

Restart/recreate the backend container after changing the variable. The allowlist is evaluated on each admin authorization check.

## Database migration

Run from the backend container or the backend deployment environment:

```bash
alembic upgrade head
```

This applies revision `0003_roles_audit`, adding `users.role` and `audit_logs`. Existing accounts receive the `user` role by default; the configured allowlist grants the initial administrator access without a public role-escalation endpoint.

## Verify

Log in using the configured account, then request `GET /api/admin/me` with the session cookie. It should return `role: admin`. A normal account should receive HTTP 403.

Keep `ADMIN_EMAILS` private. Do not send it to the browser, put it in `VITE_*` variables, or add it to Git.
