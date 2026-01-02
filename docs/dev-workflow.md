# Dev Workflow（作業手順テンプレ）

目的: 調査→計画→最小差分実装→品質ゲート→PR までを漏れなく実行する。

---

## 0) 前提チェック（ローカル）
```bash
git switch main
git pull --rebase
```

---

## 1) 調査（Investigate）
- 対象コード/テンプレ/既存エンドポイント/既存クエリを把握する
- 必ず検索して既存実装を再利用する（重複実装禁止）
  - 例: `rg "keyword"` / `rg "template_name"` / `rg "router"`

調査メモ（PR本文に転記できる形で残す）:
- 見たファイル:
- 検索ワード:
- 既存の類似実装:

---

## 2) 計画（Plan）
- 変更点を箇条書き（影響範囲、DB変更の有無、テスト方針）
- セキュリティ低下/破壊的変更がないことを明記
- DB変更がある場合は Alembic 方針（revision名、upgrade/downgrade）を先に書く

---

## 3) ブランチ作成（必須）
Issueがある場合:
```bash
gh issue view <番号>
git switch -c <type>/issue-<番号>-<short-slug>
```

Issueがない場合:
```bash
git switch -c <type>/<short-slug>
```

命名規約は docs/branching-commit.md を参照。

---

## 4) 実装（Implement）
- 最小差分で実装する
- 既存命名・既存構造・既存パターンを踏襲する
- 秘密情報をログ/例外/テンプレに出さない（必要ならマスクする）
- htmxのエンドポイントは「部分HTML返却」を前提に、通常遷移と混同しない

---

## 5) Lint / Format（ruff）
```bash
uv run ruff check .
# format導入済みの場合のみ
uv run ruff format .
```

---

## 6) Test（pytest）
```bash
uv run pytest -q
```

---

## 7) DB変更がある場合（Alembic）
```bash
uv run alembic revision --autogenerate -m "add_xxx_to_yyy"
# 生成物レビュー（意図しないDROP/ALTERがないか）
uv run alembic upgrade head
```

---

## 8) コミット（日本語必須）
- コミットメッセージは日本語、秘密情報禁止
- 変更を詰め込みすぎずレビュー可能な単位に分割する  
  規約は docs/branching-commit.md を参照。

---

## 9) push → PR作成（gh）
```bash
git push -u origin HEAD
gh pr create --fill
```

---

## 10) 報告（PR本文/Claude出力）
CLAUDE.md の Output Format（Plan/Changes/Verification/Notes）に従い、以下を必ず明記する。
- 実行したコマンドと結果
- 未実行は「未実行」
