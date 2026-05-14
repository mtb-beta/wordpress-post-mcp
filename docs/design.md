# 機能設計

MCP ツールとして提供する各機能の引数・返り値の設計です。

提供するツールは以下の5つです。

- `create_draft` — 下書き保存
- `list_posts` — 記事一覧の取得・検索
- `get_post` — 記事の詳細取得
- `list_categories` — カテゴリ一覧の取得
- `list_tags` — タグ一覧の取得

---

## `create_draft` — 下書き保存

タイトルと本文を指定して WordPress に下書きを作成します。ステータスは常に `draft` で固定し、公開はしません。

### 引数

| 名前 | 型 | 必須 | 説明 |
|------|-----|:----:|------|
| `title` | string | ✓ | 記事タイトル |
| `content` | string | ✓ | 記事本文（Markdown）。MCP 側で HTML に変換して保存する |
| `excerpt` | string | | 抜粋 |
| `slug` | string | | URL スラッグ |
| `category_ids` | number[] | | カテゴリ ID のリスト |
| `tag_ids` | number[] | | タグ ID のリスト |

### 返り値

```json
{
  "id": 123,
  "title": "記事タイトル",
  "status": "draft",
  "link": "https://your-site.com/?p=123"
}
```

### 補足

- Markdown は CommonMark を基本とする。実装コストが増えなければ GFM まで対応する。
- WordPress ショートコード（`[caption]` など）や独自ブロック記法は対象外。
- コードブロックは `<pre><code>` で素朴に出力し、シンタックスハイライトは WordPress 側に任せる。
- 同一タイトルの既存記事があっても重複作成を許可する（警告は出さない）。
- `excerpt` を省略した場合は WordPress 側の自動生成に任せる（本文から自動で抜粋が作られる）。

---

## `list_posts` — 記事一覧の取得・検索

投稿済み・下書き記事の一覧を、フィルタ条件およびキーワードで取得します。

### 引数

| 名前 | 型 | 必須 | 説明 |
|------|-----|:----:|------|
| `query` | string | | 検索キーワード（タイトル・本文を全文検索） |
| `status` | string | | `publish` / `draft` / `any`。デフォルト: `any` |
| `category_id` | number | | カテゴリ ID で絞り込み |
| `tag_id` | number | | タグ ID で絞り込み |
| `order` | string | | `asc` / `desc`（投稿日順）。デフォルト: `desc` |
| `per_page` | number | | 1〜100。デフォルト: 10 |
| `page` | number | | デフォルト: 1 |

### 返り値

```json
{
  "posts": [
    {
      "id": 123,
      "title": "記事タイトル",
      "status": "publish",
      "date": "2024-01-15T10:00:00",
      "categories": [{ "id": 1, "name": "技術" }],
      "tags": [{ "id": 5, "name": "Python" }],
      "excerpt": "記事の抜粋..."
    }
  ],
  "total": 123,
  "total_pages": 13,
  "page": 1,
  "per_page": 10
}
```

### 補足

- 本文（`content`）は含めない。本文が必要な場合は `get_post` を使う（トークン消費を抑えるため）。
- `total` / `total_pages` は WordPress REST API の `X-WP-Total` / `X-WP-TotalPages` ヘッダから取得する。
- `query` と他のフィルタ（`status` / `category_id` / `tag_id`）は AND で組み合わさる。
- `status: any` を指定すると下書きと公開済みが混在する。WordPress の仕様上、日付未指定の下書きの `date` は編集のたびに更新されるため、結果として「最近作業した順」に近い並びになる。過去の公開記事を探したい場合は `status: publish` を指定するのが確実。

---

## `get_post` — 記事の詳細取得

指定 ID の記事の本文・カテゴリ・タグ・メタ情報を取得します。

### 引数

| 名前 | 型 | 必須 | 説明 |
|------|-----|:----:|------|
| `post_id` | number | ✓ | 取得する記事の ID |

### 返り値

```json
{
  "id": 123,
  "title": "記事タイトル",
  "content": "<p>本文HTML...</p>",
  "status": "publish",
  "date": "2024-01-15T10:00:00",
  "categories": [{ "id": 1, "name": "技術" }],
  "tags": [{ "id": 5, "name": "Python" }],
  "link": "https://your-site.com/post-slug/"
}
```

---

## `list_categories` — カテゴリ一覧の取得

WordPress に登録されているカテゴリの一覧を取得します。

### 引数

なし

### 返り値

```json
[
  {
    "id": 1,
    "name": "技術",
    "slug": "tech",
    "count": 42
  }
]
```

---

## `list_tags` — タグ一覧の取得

WordPress に登録されているタグの一覧を取得します。

### 引数

なし

### 返り値

```json
[
  {
    "id": 5,
    "name": "Python",
    "slug": "python",
    "count": 18
  }
]
```

---

## エラー処理

認証エラー・権限不足・ネットワークエラー・パラメータ不正などは、MCP プロトコルのエラーとして返す。ツール返り値の中にエラーを埋め込む形式は採用しない。

---

## カテゴリ・タグの ID 解決フロー

エージェントが新規記事を作成する際、`create_draft` の `category_ids` / `tag_ids` に渡す ID は事前に解決しておく必要がある。想定するフローは以下の通り。

1. `list_categories` / `list_tags` で利用可能な分類を取得
2. 既存記事を参考にしたい場合は `list_posts` / `get_post` で参照（返り値に `id` と `name` の両方が含まれる）
3. 適切な ID を選んで `create_draft` を呼ぶ
