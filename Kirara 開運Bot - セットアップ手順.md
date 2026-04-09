# Kirara 開運Bot - Windowsセットアップ手順

## 概要

このシステムは2つのスクリプトで構成されています。

| スクリプト | 機能 |
|---|---|
| `kirara_bot.py` | Xへの自動投稿（毎日朝9時・夜21時） |
| `note_generator.py` | note記事の自動生成（週1回・手動実行） |

使用するAI：**Google AI Studio（Gemini API）** ← 無料で使えます

---

## ステップ1：Gemini APIキーを取得する

1. [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) を開く
2. Googleアカウントでログイン
3. 「**APIキーを作成**」をクリック
4. 表示されたキー（`AIza...`から始まる文字列）をコピーして保存

---

## ステップ2：Pythonをインストールする

1. [https://www.python.org/downloads/](https://www.python.org/downloads/) を開く
2. 「Download Python 3.x.x」をクリックしてダウンロード
3. インストーラーを起動
4. **「Add Python to PATH」にチェックを入れる**（重要！）
5. 「Install Now」をクリック

---

## ステップ3：ファイルを準備する

1. デスクトップに `kirara_bot` というフォルダを作る
2. 以下の3つのファイルをそのフォルダに入れる：
   - `kirara_bot.py`
   - `note_generator.py`
   - `.env.example`

---

## ステップ4：.envファイルを作る

1. `.env.example` をコピーして、名前を `.env` に変更する
   - ※ Windowsでは拡張子なしのファイルを作るため、メモ帳で新規作成して「すべてのファイル」で保存するのが確実
2. `.env` をメモ帳で開き、各キーを入力する：

```
X_API_KEY=（コンシューマーキー）
X_API_SECRET=（シークレットキー）
X_ACCESS_TOKEN=（アクセストークン）
X_ACCESS_TOKEN_SECRET=（アクセストークンシークレット）
GEMINI_API_KEY=（Google AI StudioのAPIキー）
```

---

## ステップ5：必要なライブラリをインストールする

1. `kirara_bot` フォルダの中で右クリック →「ターミナルで開く」
   （またはコマンドプロンプトを開いて `cd デスクトップ\kirara_bot` と入力）
2. 以下のコマンドを実行：

```
pip install tweepy google-generativeai schedule python-dotenv
```

---

## ステップ6：テスト投稿をする

```
python kirara_bot.py --test
```

投稿文が表示されるので、内容を確認して「y」を押すと実際にXに投稿されます。

---

## ステップ7：自動投稿を開始する

```
python kirara_bot.py
```

毎日9:00と21:00に自動投稿されます。
**このウィンドウを開いたままにしておく必要があります。**
PCをスリープ・シャットダウンすると止まります。

---

## note記事の生成

```
python note_generator.py
```

`note_drafts` フォルダにMarkdownファイルが保存されます。
メモ帳で開いて内容を確認・編集してからnoteに投稿してください。

---

## 投稿スケジュール

| 時間 | 内容 |
|---|---|
| 毎朝 9:00 | 今日のテーマ別開運メッセージ（曜日ごとに変わる） |
| 毎夜 21:00 | 夜の浄化・明日への開運メッセージ |
| 週1回（手動） | note記事の生成・投稿 |

---

## 注意事項

- `.env` ファイルは絶対に他人に見せないでください
- APIキーが漏れた場合はすぐに再発行してください
- X APIの利用料は1日2回投稿で約3円/日（月約90円）です
- Gemini APIは無料枠内で十分まかなえます（月数十円以下）
