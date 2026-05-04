# Rakuten Books Management API

楽天ブックスAPIと連携し、蔵書データを効率的に管理するためのバックエンドシステムです。
単なる機能実装に留まらず、**「システム運用と開発の両面から見た保守性の高さ」**をコンセプトに設計しています。

## 🚀 プロジェクトの背景
個人で所有する約3,000冊の蔵書管理を自動化するために開発。
「検索で見つからなかった書籍をどう扱うか」「外部APIが不安定な時にどう挙動すべきか」といった、実務で直面する課題に対する解をコードに反映させています。

## 🛠 技術スタック
- **Framework**: FastAPI (Python 3.12+)
- **ORM**: SQLAlchemy 2.0 (Async mode)
- **Database**: SQLite
- **API Client**: httpx (Asynchronous)
- **Validation**: Pydantic v2
- **CLI Utilities**: tqdm (Progress Bar)
- **Environment**: Vim / Ruff (Linter & Formatter)

## ✨ こだわり・設計のポイント

### 1. 実務的なエラーハンドリングと障害切り分け
システム運用の経験を活かし、エラー発生時の原因特定を迅速化する設計を行っています。
- **例外の具体化**: `Exception` による一括キャッチを避け、`httpx.HTTPStatusError` や `SQLAlchemyError` など、原因に応じた適切な例外処理を実装。
- **エラーメッセージの可視化**: 楽天APIが返したエラー詳細（レスポンスボディ）をキャッチし、そのままAPIレスポンスの `detail` に含めることで、フロントエンドや運用者が即座に原因を把握できるようにしています。

### 2. データの網羅性を担保する仕様
API検索の結果、書籍が見つからなかった場合でも、ISBNをキーとして `get_flg=False` 状態でレコードを作成します。
これにより、「システム内に登録はあるが、詳細データが未取得である」という状態を管理でき、将来的な再取得や手動登録のトリガーとして活用可能です。

### 3. データ移行・メンテナンス用スクリプトの完備
既存DBの不完全なデータ（出版者記号・書名記号のみ）を自動でISBN13へ変換し、自作APIを通じて一括登録するメンテナンススクリプトを同梱しています。
- **堅牢な変換ロジック**: Pydanticを用いたバリデーションにより、不正な記号を含むデータを事前に排除。
- **一括処理（バッチ）最適化**: `httpx` の非同期通信とバッチ送信（50件単位など）により、大量データも高速に同期。
- **進捗の可視化**: `tqdm` によるプログレスバー表示を実装し、長時間かかる処理の視認性を確保。

## 📂 ディレクトリ構造
```text
src/
├── app/
│   ├── api/
│   │   └── v1/            # APIエンドポイント定義（バージョニング）
│   ├── core/              # 設定・共通処理
│   ├── models/            # SQLAlchemy DBモデル
│   ├── schemas/           # Pydanticデータ定義
│   ├── scripts/           # メンテナンス・データ移行用スクリプト（追加）
│   │   └── import_books.py
│   ├── services/          # 楽天API連携ロジック（Service層）   
│   └── main.py            # エントリーポイント
```

## ⚙️ セットアップ
```bash
# 1．クローン
git clone https://github.com/koma000/rakuten-books-app.git
cd rakuten-books-app

# 2. 依存関係のインストール (Poetryを使用)
poetry install

# 3. 環境変数の設定
cat << EOF > .env
RAKUTEN_APPLICATION_ID=あなたのアプリケーションID
RAKUTEN_ACCESS_KEY=あなたのアクセスキー
SRC_DB_PATH=移行元DBのパス
EOF

# 4. サーバー起動
poetry run uvicorn src.app.main:app --reload
```

## 🛠 スクリプトの実行
既存DBから情報を抽出し、API経由で書籍データを登録・更新します。サーバー（uvicorn）を起動した状態で実行してください。

```bash
# ISBN変換およびAPI一括同期の実行
poetry run python -m src.app.scripts.import_books
```

---