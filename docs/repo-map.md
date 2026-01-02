# Repo Map（構造メモ）

注意: ここは「実構造に合わせて更新する」ためのメモ。
不確実な情報は CLAUDE.md に置かず、このファイルに集約する。

---

## 例（要更新）
- app/
  - main.py: FastAPI エントリポイント（例: app.main:app）
  - templates/: Jinja2 テンプレート
  - static/: CSS/JS等（htmxはCDN想定）
  - db/ または models/: SQLAlchemyモデル、DBセッション管理
  - routes/ または routers/: ルーティング
  - services/: ビジネスロジック層（存在すれば）
- alembic/
  - versions/: マイグレーション
  - env.py: マイグレーション環境
- tests/: pytest
- .env.example: 環境変数例（秘密情報は禁止）
- pyproject.toml: 依存/ruff/pytest設定（uv運用）

---

## 更新TODO（見つけたら直す）
- app配下の実ディレクトリ（routers/templates/db等）を実態に合わせる
- 主要エントリポイント、設定ファイルの場所を確定する
