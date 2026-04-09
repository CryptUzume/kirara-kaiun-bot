# GitHub Actions セットアップ手順

kirara_botをGitHub Actionsで自動投稿するための手順です。
**所要時間：約15分**（GitHubアカウントがある前提）

---

## STEP 1：GitHubアカウントを作成する（持っている場合はスキップ）

[https://github.com/signup](https://github.com/signup) から無料で作成できます。

---

## STEP 2：新しいリポジトリを作成する

1. [https://github.com/new](https://github.com/new) を開く
2. 以下のように設定する：
   - **Repository name**：`kirara-kaiun-bot`
   - **Visibility**：`Private`（プライベートを選択）
   - **Initialize this repository with a README**：チェックしない
3. 「Create repository」ボタンをクリック

---

## STEP 3：ファイルをアップロードする

添付のZIPファイル（`kirara_bot_github.zip`）を解凍すると、以下のフォルダ構成になっています：

```
kirara_bot/
├── kirara_bot.py          ← メインのBotスクリプト
├── requirements.txt       ← 必要なパッケージ一覧
├── .env.example           ← APIキーのサンプル
├── .gitignore             ← Gitに含めないファイルの設定
└── .github/
    └── workflows/
        └── auto_post.yml  ← GitHub Actionsの設定ファイル
```

### アップロード方法（コマンドライン）

PowerShellで以下を実行してください：

```powershell
# ZIPを解凍したフォルダに移動（パスは実際の場所に合わせてください）
cd C:\Users\silve\kirara_bot

# Gitの初期設定（初回のみ）
git config --global user.email "あなたのメールアドレス"
git config --global user.name "あなたの名前"

# Gitリポジトリを初期化してプッシュ
git init
git add .
git commit -m "初回コミット"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/kirara-kaiun-bot.git
git push -u origin main
```

> **注意**：`git push` 時にGitHubのユーザー名とパスワード（またはPersonal Access Token）を求められます。

---

## STEP 4：APIキーをGitHub Secretsに登録する

**これが最重要ステップです。** `.env`ファイルはGitHubにアップしてはいけないので、代わりにGitHub Secretsに登録します。

1. GitHubのリポジトリページを開く
2. 上部タブの「**Settings**」をクリック
3. 左メニューの「**Secrets and variables**」→「**Actions**」をクリック
4. 「**New repository secret**」ボタンをクリック
5. 以下の5つを1つずつ登録する：

| Name（名前） | Secret（値） |
|---|---|
| `OPENAI_API_KEY` | OpenAIのAPIキー |
| `X_API_KEY` | X DeveloperのAPI Key |
| `X_API_SECRET` | X DeveloperのAPI Key Secret |
| `X_ACCESS_TOKEN` | X DeveloperのAccess Token |
| `X_ACCESS_TOKEN_SECRET` | X DeveloperのAccess Token Secret |

---

## STEP 5：動作確認（手動実行）

1. GitHubのリポジトリページで「**Actions**」タブをクリック
2. 左側に「Kirara 開運Bot 自動投稿」が表示されていることを確認
3. 「**Run workflow**」ボタンをクリック
4. `time_of_day`を「morning」にして「Run workflow」を実行
5. 緑のチェックマークが付けば成功！

---

## 自動投稿のスケジュール

設定完了後は、以下のスケジュールで自動投稿されます：

| 時刻 | 内容 |
|---|---|
| 毎日 9:00 JST | 朝の開運メッセージ |
| 毎日 21:00 JST | 夜の開運メッセージ |

**料金目安：** 1日2投稿 × 30日 = 月$0.60（約90円）

---

## トラブルシューティング

### Actionsが動かない場合
- リポジトリの「Settings」→「Actions」→「General」で「Allow all actions」が選択されているか確認

### 投稿エラーが出る場合
- GitHub Secretsのキー名が正確か確認（大文字・小文字も一致させる）
- X Developer PortalでApp permissionsが「Read and Write」になっているか確認
- クレジット残高が0になっていないか確認

### GitHub Actionsのログを確認する方法
1. 「Actions」タブをクリック
2. 実行されたワークフローをクリック
3. 「post」ジョブをクリック
4. 各ステップのログを確認
