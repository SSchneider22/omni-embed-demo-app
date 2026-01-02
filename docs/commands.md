# Commands（uv / alembic / uvicorn / ruff / pytest / gh）

注意: 実際の設定は README / pyproject.toml / alembic.ini を優先する（このファイルは“手元で叩く候補”の一覧）。

---

## セットアップ
```bash
uv sync
cp .env.example .env
# .env に認証情報を設定（値は絶対に共有/コミットしない）
uv run alembic upgrade head
```

---

## 開発サーバ
```bash
uv run uvicorn app.main:app --reload
# http://localhost:8000
```

---

## Lint / Format
```bash
uv run ruff check .
# format導入済みの場合のみ（pyproject.tomlで確認）
uv run ruff format .
```

---

## テスト
```bash
uv run pytest -q
```

---

## マイグレーション（DB変更がある場合）
```bash
uv run alembic revision --autogenerate -m "describe_change"
# 生成物をレビュー（意図しないDROP/ALTERがないか確認）
uv run alembic upgrade head
```

---

## GitHub CLI（PR/Issue）
```bash
gh issue view <番号>
gh pr create --fill
gh pr view --web
```

---

## よくある失敗と切り分け

### `gh` が認証できない
```bash
gh auth status
gh auth login
```

### `gh pr create` が失敗
- push漏れ、remote未設定、既定ブランチ名不一致（main/master）を確認

### `alembic upgrade` が失敗
- `.env` / DB URL設定を確認
- 意図しないマイグレーション差分（DROP/ALTER）が出ていないか確認

### `uvicorn` 起動で import error
- `app.main:app` のパスが正しいか
- `__init__.py` の有無
- 作業ディレクトリがリポジトリルートになっているか
