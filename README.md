# Omni Embed Demo App

会員向け購買分析レポート（Omni Embed）閲覧アプリ - MVP

## 技術スタック

- **Backend**: FastAPI + Jinja2
- **Frontend**: htmx (CDN)
- **Database**: SQLite
- **ORM**: SQLAlchemy 2.x + Alembic
- **依存管理**: uv
- **Embed**: Omni Embed (Standard SSO - manual generation)

### 技術選定理由

- **SQLAlchemy 2.x + Alembic**: 型安全なORM、マイグレーション管理、SQLite→PostgreSQL移行が容易
- **uv**: 高速なPython依存管理ツール、pip/pipenvの代替
- **htmx**: JavaScriptフレームワーク不要で動的UI実装可能、Node.js不要

## セットアップ

### 前提条件

- Python 3.12+
- uv (https://github.com/astral-sh/uv)

### インストール

```bash
# 依存関係のインストール
uv sync

# 環境変数設定
cp .env.example .env
# .envを編集してOmni認証情報を設定

# データベースマイグレーション
uv run alembic upgrade head
```

### 起動

```bash
uv run uvicorn app.main:app --reload
```

アプリケーションは http://localhost:8000 で起動します。

## 機能

- ユーザー登録
- ログイン/ログアウト（HttpOnlyセッションCookie）
- マイページ
- Omni Embedレポート表示（Standard SSO）
- 監査ログ

## セキュリティ

- パスワードハッシュ（argon2）
- HttpOnlyセッションCookie
- CSRF対策
- レート制限
- 列挙対策
- 環境変数管理（.envは非コミット）

## ID体系

- ログインID: `email`
- 顧客識別子: `customer_id`（VARCHAR）
- Omni RLS: `customer_id`のみ使用
- Omni `externalId`: `customer_id`を使用

## ライセンス

MIT
