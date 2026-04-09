"""
Kirara 開運Bot - X自動投稿システム（X API Pay-Per-Use版）
========================================
八百万の神様からのメッセージを毎日自動投稿します。
OpenAI API（gpt-4.1-mini）で文章生成 → X API（Pay-Per-Use）で投稿します。

【X API Pay-Per-Use料金】
  投稿1件 = $0.01（約1.5円）
  1日2投稿 × 30日 = 月60件 = $0.60（約90円/月）
  ※最初に$5分のクレジットを購入すれば約8ヶ月分

【初回セットアップ】
  1. https://developer.x.com でDeveloper Portalにアクセス
  2. 「Pay-Per-Use」プランを選択してクレジットを購入（最低$5）
  3. アプリのApp permissionsを「Read and Write」に設定
  4. アクセストークンを再発行して.envに設定

【使い方】
  python kirara_bot.py --generate          # 投稿文を生成して表示するだけ（テスト・無料）
  python kirara_bot.py --test              # 生成して実際にXに1件投稿（$0.01消費）
  python kirara_bot.py --bulk 7            # 7日分の投稿文をCSVに出力（投稿はしない）
  python kirara_bot.py                     # 毎日9時・21時に自動投稿
"""

import os
import sys
import random
import csv
import datetime
import tweepy
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# ========================================
# 設定
# ========================================

MORNING_THEMES = [
    "恋愛・縁結び",
    "金運・財運",
    "仕事・転職",
    "人間関係・対人運",
    "健康・体調",
    "直感・決断",
    "チャレンジ・新しい挑戦",
]

EVENING_THEMES = [
    "今日の振り返りと明日への開運",
    "夜の浄化と心の癒し",
    "眠る前の感謝と開運",
    "明日の準備と神様からのアドバイス",
    "夜の縁結び・恋愛運",
    "金運を引き寄せる夜の習慣",
    "自分を大切にする夜のメッセージ",
]

GODS = {
    "恋愛・縁結び": ["大国主命（おおくにぬしのみこと）", "磐長姫（いわながひめ）", "木花咲耶姫（このはなさくやひめ）"],
    "金運・財運": ["大黒天（だいこくてん）", "恵比寿様（えびすさま）", "稲荷大神（いなりおおかみ）"],
    "仕事・転職": ["天照大御神（あまてらすおおみかみ）", "武甕槌神（たけみかづちのかみ）", "大己貴神（おおなむちのかみ）"],
    "人間関係・対人運": ["大国主命（おおくにぬしのみこと）", "事代主神（ことしろぬしのかみ）", "豊受大神（とようけのおおかみ）"],
    "健康・体調": ["大山津見神（おおやまつみのかみ）", "少彦名命（すくなびこなのみこと）", "大己貴神（おおなむちのかみ）"],
    "直感・決断": ["天照大御神（あまてらすおおみかみ）", "瀬織津姫（せおりつひめ）", "猿田彦大神（さるたひこのおおかみ）"],
    "チャレンジ・新しい挑戦": ["建速須佐之男命（たけはやすさのおのみこと）", "天之御中主神（あめのみなかぬしのかみ）", "武甕槌神（たけみかづちのかみ）"],
    "今日の振り返りと明日への開運": ["天照大御神（あまてらすおおみかみ）", "月読命（つくよみのみこと）"],
    "夜の浄化と心の癒し": ["瀬織津姫（せおりつひめ）", "月読命（つくよみのみこと）"],
    "眠る前の感謝と開運": ["豊受大神（とようけのおおかみ）", "大国主命（おおくにぬしのみこと）"],
    "明日の準備と神様からのアドバイス": ["天照大御神（あまてらすおおみかみ）", "猿田彦大神（さるたひこのおおかみ）"],
    "夜の縁結び・恋愛運": ["大国主命（おおくにぬしのみこと）", "磐長姫（いわながひめ）"],
    "金運を引き寄せる夜の習慣": ["大黒天（だいこくてん）", "稲荷大神（いなりおおかみ）"],
    "自分を大切にする夜のメッセージ": ["木花咲耶姫（このはなさくやひめ）", "天照大御神（あまてらすおおみかみ）"],
}

HASHTAGS = {
    "恋愛・縁結び": "#恋愛運 #縁結び #神様からのメッセージ #開運 #占い",
    "金運・財運": "#金運 #財運 #開運 #神様からのメッセージ #占い",
    "仕事・転職": "#仕事運 #転職 #開運 #神様からのメッセージ #占い",
    "人間関係・対人運": "#人間関係 #対人運 #開運 #神様からのメッセージ #占い",
    "健康・体調": "#健康運 #開運 #神様からのメッセージ #占い",
    "直感・決断": "#直感 #開運 #神様からのメッセージ #占い",
    "チャレンジ・新しい挑戦": "#開運 #神様からのメッセージ #占い #チャレンジ",
    "今日の振り返りと明日への開運": "#開運 #神様からのメッセージ #夜の占い",
    "夜の浄化と心の癒し": "#浄化 #癒し #開運 #神様からのメッセージ",
    "眠る前の感謝と開運": "#開運 #感謝 #神様からのメッセージ #夜の占い",
    "明日の準備と神様からのアドバイス": "#開運 #神様からのメッセージ #明日の運勢",
    "夜の縁結び・恋愛運": "#恋愛運 #縁結び #開運 #神様からのメッセージ",
    "金運を引き寄せる夜の習慣": "#金運 #開運 #神様からのメッセージ",
    "自分を大切にする夜のメッセージ": "#開運 #自己愛 #神様からのメッセージ #癒し",
}

# ========================================
# AI投稿文生成（OpenAI API）
# ========================================

def generate_post(theme: str, time_of_day: str = "朝") -> str:
    """OpenAI APIを使って投稿文を生成する"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEYが設定されていません。.envファイルを確認してください。")

    client = OpenAI(api_key=api_key)

    gods_list = GODS.get(theme, ["八百万の神々"])
    god = random.choice(gods_list)
    hashtags = HASHTAGS.get(theme, "#開運 #神様からのメッセージ #占い")

    prompt = f"""あなたは日本の神道・スピリチュアルの世界観を持つ占い師「Kirara」です。
八百万の神々からのメッセージを受け取り、フォロワーに届けます。

以下の条件でXの投稿文を1つ作成してください。

【テーマ】{theme}
【時間帯】{time_of_day}
【今日のメッセージを届ける神様】{god}
【文字数】120文字以内（ハッシュタグ除く）
【トーン】温かく、寄り添う。でも神秘的で引き込まれる雰囲気。
【絵文字】⛩️✨🌸🕊️🌙🌟などを1〜3個使う。多用しない。
【改行ルール】必ず2〜3行に分けて書く。1文ごとに改行を入れ、読みやすくする。
  例：
  朝の光が静かに降り注ぐ今日。\n
  天照大御神があなたに伝えるのは、「焦らなくていい」という言葉。\n
  あなたのペースで、確かに前へ進んでいる。✨
【禁止事項】「今日の運勢は〜」のような単調な書き出しは避ける。読んだ人が「私のことだ」と感じる書き方にする。一行にまとめない。

本文の最後に空行を入れてから以下のハッシュタグを付ける：
{hashtags}

投稿文のみを出力すること。説明や前置きは不要。"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.9,
    )
    return response.choices[0].message.content.strip()


# ========================================
# X投稿（Tweepy / X API v2）
# ========================================

def post_to_x(text: str) -> dict:
    """
    X API（Pay-Per-Use）を使ってXに投稿する。
    料金：1件 $0.01（約1.5円）
    """

    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError(
            "X APIキーが設定されていません。.envファイルを確認してください。\n"
            "必要なキー: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET"
        )

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    response = client.create_tweet(text=text)
    return response.data


# ========================================
# 毎日の投稿実行
# ========================================

def morning_post():
    """朝の投稿（9時）"""
    day_of_week = datetime.datetime.now().weekday()
    theme = MORNING_THEMES[day_of_week % len(MORNING_THEMES)]
    print(f"[朝の投稿] テーマ: {theme}")
    text = generate_post(theme, "朝")
    print(f"生成された投稿:\n{text}\n")
    result = post_to_x(text)
    print(f"投稿完了！ Tweet ID: {result['id']}")
    return result


def evening_post():
    """夜の投稿（21時）"""
    day_of_week = datetime.datetime.now().weekday()
    theme = EVENING_THEMES[day_of_week % len(EVENING_THEMES)]
    print(f"[夜の投稿] テーマ: {theme}")
    text = generate_post(theme, "夜")
    print(f"生成された投稿:\n{text}\n")
    result = post_to_x(text)
    print(f"投稿完了！ Tweet ID: {result['id']}")
    return result


# ========================================
# メイン
# ========================================

if __name__ == "__main__":

    # 生成のみモード（投稿しない・完全無料）
    if "--generate" in sys.argv:
        print("=" * 50)
        print("生成のみモード：投稿文を表示します（Xには投稿しません）")
        print("=" * 50)
        for theme in MORNING_THEMES[:3]:
            print(f"\n【テーマ: {theme}】")
            text = generate_post(theme, "朝")
            print(text)
            print("-" * 40)
        sys.exit(0)

    # テストモード（生成して実際に1回投稿・$0.01消費）
    if "--test" in sys.argv:
        print("=" * 50)
        print("テストモード：生成して実際にXに投稿します（$0.01消費）")
        print("=" * 50)
        theme = random.choice(MORNING_THEMES)
        print(f"テーマ: {theme}")
        text = generate_post(theme, "朝")
        print(f"\n生成された投稿文:\n{text}\n")
        confirm = input("この内容でXに投稿しますか？ (y/n): ")
        if confirm.lower() == "y":
            try:
                result = post_to_x(text)
                print(f"\n投稿完了！ Tweet ID: {result['id']}")
                print(f"確認URL: https://x.com/Kirara_kaiun/status/{result['id']}")
            except tweepy.errors.Forbidden as e:
                print(f"\nエラー: 投稿できませんでした。")
                print(f"原因: {e}")
                print("\n【解決方法】")
                print("X Developer Portalで以下を確認してください:")
                print("1. Pay-Per-Useプランに切り替えてクレジット（最低$5）を購入")
                print("2. App permissionsが「Read and Write」になっているか確認")
                print("3. アクセストークンをApp permissions変更後に再発行")
                print("詳細: https://developer.x.com/en/portal/dashboard")
            except Exception as e:
                print(f"\nエラー: {e}")
        else:
            print("投稿をキャンセルしました。")
        sys.exit(0)

    # まとめ生成モード（CSVに出力・投稿はしない）
    if "--bulk" in sys.argv:
        try:
            idx = sys.argv.index("--bulk")
            days = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 7
        except (ValueError, IndexError):
            days = 7

        print("=" * 50)
        print(f"まとめ生成モード：{days}日分の投稿文をCSVに出力します（Xには投稿しません）")
        print("=" * 50)

        rows = []
        for i in range(days):
            morning_theme = MORNING_THEMES[i % len(MORNING_THEMES)]
            evening_theme = EVENING_THEMES[i % len(EVENING_THEMES)]

            print(f"\n--- {i + 1}日目 ---")

            print(f"[朝] テーマ: {morning_theme} 生成中...")
            morning_text = generate_post(morning_theme, "朝")
            rows.append({"時間帯": "朝（9:00）", "テーマ": morning_theme, "投稿文": morning_text})
            print(morning_text[:50] + "...")

            print(f"[夜] テーマ: {evening_theme} 生成中...")
            evening_text = generate_post(evening_theme, "夜")
            rows.append({"時間帯": "夜（21:00）", "テーマ": evening_theme, "投稿文": evening_text})
            print(evening_text[:50] + "...")

        # CSVに出力
        output_file = f"posts_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["時間帯", "テーマ", "投稿文"])
            writer.writeheader()
            writer.writerows(rows)

        print(f"\n{'=' * 50}")
        print(f"完了！ {len(rows)}件の投稿文を {output_file} に出力しました")
        print(f"\n【次のステップ】")
        print(f"このCSVを開いて投稿文を確認し、Xの予約投稿機能で手動スケジュールするか、")
        print(f"python kirara_bot.py --test で1件ずつ確認しながら投稿してください。")
        sys.exit(0)

    # GitHub Actions用：--post morning / --post evening
    if "--post" in sys.argv:
        try:
            idx = sys.argv.index("--post")
            timing = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "morning"
        except IndexError:
            timing = "morning"

        if timing == "morning":
            print("[GitHub Actions] 朝の投稿を実行します")
            morning_post()
        else:
            print("[GitHub Actions] 夜の投稿を実行します")
            evening_post()
        sys.exit(0)

    # 定期投稿モード（毎日9時・21時・自動）
    import schedule
    import time

    print("=" * 50)
    print("Kirara 開運Bot 起動（X API Pay-Per-Use版）")
    print("毎日 9:00 と 21:00 に自動投稿します")
    print("料金目安: 1日2投稿 × 30日 = 月$0.60（約90円）")
    print("停止するには Ctrl+C を押してください")
    print("=" * 50)

    schedule.every().day.at("09:00").do(morning_post)
    schedule.every().day.at("21:00").do(evening_post)

    while True:
        schedule.run_pending()
        time.sleep(60)
