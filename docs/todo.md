# TODO（未確定事項）

このファイルは「未確認/未決定」を集約する。CLAUDE.mdには不確実情報を置かない。

- `.env.example` の環境変数名（Omni関連、DB URL等）の確定と追記
- ruff format 導入有無を pyproject.toml で確認
- pytest fixture 方針（DBの作り方、TestClient有無、トランザクション戦略）の確認
- CI（GitHub Actions等）有無、CIでの実行コマンドの確認
- セキュリティ対策（CSRF/レート制限/セッション設定）の実装箇所特定とチェックリスト化
