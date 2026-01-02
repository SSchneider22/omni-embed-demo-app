# Testing & Quality（pytest / ruff）

---

## pytest 方針
- 新規機能: 最低1本テスト追加（正常系 + 重要な異常系）
- バグ修正: 回帰テストを優先して追加 → 修正
- 外部通信（Omni関連）をテストで直叩きしない（モック/スタブ）
- DBを使う場合は既存fixture/トランザクション戦略に合わせる（勝手に流儀を増やさない）

---

## 品質ゲート（必須）
PR前に実行し、結果を報告に明記（未実行なら未実行と書く）:
- `uv run ruff check .`
- `uv run pytest -q`
- format導入済みなら `uv run ruff format .`
- DB変更がある場合 `uv run alembic upgrade head`

---

## レビュー観点（最小セット）
- 最小差分になっているか
- 重複実装が増えていないか（既存検索/再利用）
- 秘密情報が出力に混ざっていないか
- DB変更にAlembicが付いているか（upgrade/downgrade整合、既存revision改変なし）
