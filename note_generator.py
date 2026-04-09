"""
Kirara note記事自動生成システム（google-genai最新版）
========================================
週1回、noteに投稿するスピリチュアル記事を自動生成します。

使い方:
  python note_generator.py           # 今週のテーマで記事を生成
  python note_generator.py --theme 恋愛  # テーマ指定で生成
"""

import os
import sys
import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

WEEKLY_THEMES = [
    {
        "title_template": "【{month}月の恋愛運】縁結びの神様が教える、今月あなたに必要なこと",
        "theme": "恋愛・縁結び",
        "keywords": ["恋愛運", "縁結び", "片思い", "復縁", "出会い"],
        "god": "大国主命（おおくにぬしのみこと）",
    },
    {
        "title_template": "【{month}月の金運】稲荷大神からのメッセージ｜お金に愛される人がやっていること",
        "theme": "金運・財運",
        "keywords": ["金運", "財運", "お金", "副業", "引き寄せ"],
        "god": "稲荷大神（いなりおおかみ）",
    },
    {
        "title_template": "あなたを守る神様はどなた？守護神の見つけ方と参拝のコツ",
        "theme": "守護神・神社参拝",
        "keywords": ["守護神", "神社", "参拝", "パワースポット", "八百万の神"],
        "god": "天照大御神（あまてらすおおみかみ）",
    },
    {
        "title_template": "【{month}月】今月行くべきパワースポット神社｜開運のサインを見逃さないで",
        "theme": "パワースポット・神社参拝",
        "keywords": ["パワースポット", "神社", "開運", "参拝", "ご利益"],
        "god": "猿田彦大神（さるたひこのおおかみ）",
    },
]


def generate_note_article(theme_data: dict) -> dict:
    """Gemini APIを使ってnote記事を生成する"""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")

    client = genai.Client(api_key=api_key)

    now = datetime.datetime.now()
    month = now.month
    title = theme_data["title_template"].format(month=month)
    theme = theme_data["theme"]
    god = theme_data["god"]
    keywords = "、".join(theme_data["keywords"])

    prompt = f"""あなたは日本の神道・スピリチュアルの世界観を持つ占い師「Kirara」です。
noteに投稿する記事を書いてください。

【タイトル】{title}
【テーマ】{theme}
【メインの神様】{god}
【キーワード】{keywords}

【記事の構成】
1. 導入（読者の悩みに共感する書き出し、200字程度）
2. 神様からのメッセージ（{god}が今月伝えたいこと、300字程度）
3. 具体的な開運アドバイス3つ（各150字程度）
4. まとめ・締め（ococonaラでの本格鑑定への自然な誘導を含む、200字程度）

【文体・トーン】
- 温かく、寄り添う。神秘的だが難しくない。
- 読者が「私のことだ」と感じるような共感ワードを使う。
- 専門用語は使わず、誰でも読みやすい文章。
- 絵文字は⛩️✨🌸🕊️🌙🌟などを適度に使う。

【締めの誘導文（必ず含める）】
「より詳しい個人鑑定はococonaラでも承っています。神様からのメッセージをあなただけにお伝えします。」

Markdown形式で出力してください。見出しは##を使用。"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )
    content = response.text.strip()

    return {
        "title": title,
        "content": content,
        "theme": theme,
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
    }


def save_article(article: dict) -> str:
    """記事をMarkdownファイルとして保存する"""

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "note_drafts")
    os.makedirs(output_dir, exist_ok=True)

    now = datetime.datetime.now()
    filename = f"{now.strftime('%Y%m%d')}_{article['theme'].replace('・', '_')}.md"
    filepath = os.path.join(output_dir, filename)

    full_content = f"""# {article['title']}

> 生成日時: {article['generated_at']}
> テーマ: {article['theme']}

---

{article['content']}

---

*この記事はKirara開運Botによって自動生成されました。投稿前に内容を確認・編集してください。*
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath


if __name__ == "__main__":

    theme_name = None
    if "--theme" in sys.argv:
        idx = sys.argv.index("--theme")
        if idx + 1 < len(sys.argv):
            theme_name = sys.argv[idx + 1]

    week_number = datetime.datetime.now().isocalendar()[1]
    theme_data = WEEKLY_THEMES[week_number % len(WEEKLY_THEMES)]

    if theme_name:
        for t in WEEKLY_THEMES:
            if theme_name in t["theme"]:
                theme_data = t
                break

    print("=" * 50)
    print(f"note記事を生成中...")
    print(f"テーマ: {theme_data['theme']}")
    print("=" * 50)

    article = generate_note_article(theme_data)
    filepath = save_article(article)

    print(f"\n記事が生成されました！")
    print(f"タイトル: {article['title']}")
    print(f"保存先: {filepath}")
    print(f"\n--- 記事プレビュー（冒頭300字）---")
    print(article['content'][:300] + "...")
    print("\nnoteに投稿する手順:")
    print("1. 上記ファイルをメモ帳などで開く")
    print("2. 内容を確認・編集する")
    print("3. noteの投稿画面にコピペして投稿する")
