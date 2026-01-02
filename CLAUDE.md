# Claude Code 運用ルール（CLAUDE.md）

対象: SSchneider22/omni-embed-demo-app（会員向け購買分析レポート閲覧アプリ / Omni Embed MVP）  
目的: Claude Code が安全かつ一貫した変更を「最小差分」で行うための憲法（不変ルール集）

参照（詳細手順/可変情報）:
- docs/dev-workflow.md（作業手順テンプレ）
- docs/commands.md（実行コマンド集）
- docs/branching-commit.md（ブランチ/コミット規約）
- docs/security.md（Omni/SSOセキュリティ）
- docs/repo-map.md（構造メモ）
- docs/testing-quality.md（テスト/品質）
- docs/todo.md（未確定事項）

---

## 最重要チェックリスト（必ず守る）
- 最小変更（Minimal Diff）・既存パターン最優先
- 実装前に必ず既存検索（rg/grep）して重複実装を避ける
- 秘密情報をログ/出力/テンプレ/コミット/テスト成果物に絶対入れない
- DB変更は必ず Alembic（revision追加、既存revision改変禁止）
- main/master へ直接コミット・直接push禁止（必ずブランチ + PR）
- ruff / pytest を実行し、結果を報告に明記（未実行なら未実行）

---

## 1. Scope（やること / やらないこと）

### やること
- FastAPI + Jinja2 + htmx（CDN）+ SQLite（SQLAlchemy 2.x）方針に沿う追加・修正
- 既存の設計・命名・ディレクトリ・実装パターンを尊重した最小差分の改修
- DB変更がある場合: Alembic マイグレーション作成/適用まで含める
- ruff / pytest による最低限の品質ゲートを通す
- Omni Embed（Standard SSO - manual generation）周辺の安全な取り扱い
- `gh` を使ったブランチ運用・PR作成フローを遵守

### やらないこと（禁止）
- 既存パターン無視の大規模リファクタ/再設計（必要なら「提案」止まり）
- 依存関係の勝手な追加（特に auth/security/ORM/template 系）
- `.env`、トークン、クライアントシークレット等の秘密情報の出力・ログ埋め込み・コミット
- Alembic を通さないDBスキーマ変更（直ALTER等）
- セキュリティ特性（認証/セッション/CSRF/レート制限等）を下げる変更
- main/master へ直接コミット/直接push

---

## 2. Golden Rules（最優先ルール）

1) 最小変更（Minimal Diff）
- 目的達成に必要な最小限の変更のみ
- 既存の関数/ルーティング/テンプレ構造を優先し、同等の新規実装を増やさない

2) 既存パターン優先（Project Conventions First）
- 追加実装は必ず既存コードの書き方に揃える
- 新しい流儀（別DI/別ORM操作/別テンプレ配置）を持ち込まない

3) 重複実装禁止（Reuse First）
- 変更前に必ず検索し、既存ヘルパ/テンプレ部品/クエリを再利用する
- 「似た処理」を増やすのではなく既存の共通処理に寄せる（ただし最小差分）

---

## 3. Security（秘密情報とSSOの基本姿勢）

### 秘密情報を絶対に出さない（最重要）
以下をログ/標準出力/例外メッセージ/コミット/テスト成果物に含めない:
- `.env` の中身、APIキー、クライアントシークレット、アクセストークン、SSO関連値
- Omni Embed の埋め込みURL（署名付き/トークン付きの可能性あり）
- Cookie値、セッションID、ユーザー識別子の生値

注意:
- デバッグ目的でも print() 禁止
- loggerでも値はマスク（先頭数文字のみ等）。必要最小限にする
- SSO/redirect等の入力は検証し、想定外を拒否する（Open Redirect対策）

詳細は docs/security.md を参照。

---

## 4. Database（Alembic 前提）
- DBスキーマ変更は必ず Alembic revision を追加し、upgrade/downgrade を対で実装する
- 既存revisionの改変は禁止（履歴破壊）
- autogenerate結果は必ずレビューし、意図しないDROP/ALTERがないことを確認する

---

## 5. Branch / PR（main直変更禁止）
- どんな変更でも必ずブランチを切る（main/master直コミット禁止）
- PR経由で取り込む（自己レビューでもPR作成必須）
- ブランチ名/コミットメッセージ規約は docs/branching-commit.md を参照

---

## 6. Quality Gates（最低限）
変更を出す前に必ず実行（未実行なら未実行と報告）:
- ruff: `uv run ruff check .`
- pytest: `uv run pytest -q`
- DB変更がある場合: `uv run alembic upgrade head`

---

## 7. Claude Code の回答フォーマット（固定）

PR/変更提案時は必ず以下の形式・順序で出力する。

### Plan
- 何をどう変えるか（最小差分で）
- 既存検索結果（どこを見たか / 何で検索したか）
- DB変更の有無（ある場合はmigration方針）
- ブランチ名（Issueがあれば命名規則に従う）

### Changes
- 変更ファイル一覧
- 重要な変更点の要約（箇条書き）
- 秘密情報が混入しない工夫（該当する場合）

### Verification
- 実行したコマンドと結果（未実行なら「未実行」）
  - `uv run ruff check .`：OK / 未実行
  - `uv run ruff format .`：OK / 未実行（導入済みの場合のみ）
  - `uv run pytest -q`：OK / 未実行
  - `uv run alembic upgrade head`：OK / 未実行（DB変更時）

### Notes
- 既知のリスク、互換性、運用上の注意
- TODOが残る場合は明示（何を確認すべきか）
