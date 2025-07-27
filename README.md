# YouTube to MP3 Converter LINE Bot

YouTube の URL を LINE で送信すると、音声を MP3 に変換して返してくれる LINE ボットです。

---

## 機能

- LINE で送った YouTube 動画の URL を受け取り
- サーバー側で`ffmpeg`を使って動画から音声を MP3 に変換
- 変換した MP3 ファイルを LINE に返信

---

## 動作環境・前提条件

- Python 3.8 以上
- `ffmpeg`のインストールが必須です

  - `ffmpeg`は YouTube 動画の音声変換に使用します
  - インストール方法は OS によって異なりますが、
    - macOS：`brew install ffmpeg`
    - Ubuntu：`sudo apt-get install ffmpeg`
    - Windows：公式サイトからバイナリをダウンロードしパスを通す必要があります

- LINE Messaging API のアカウントを用意し、

  - Channel Secret
  - Channel Access Token
    を取得してください。

- 開発・ローカルテスト時は`ngrok`などでローカルサーバーを外部公開し、LINE の Webhook URL に設定してください。

---

## セットアップ

1. リポジトリをクローン
   ```bash
   git clone https://github.com/Kento3019/youtube-to-mp3_v2.git
   cd youtube-to-mp3_v2
   ```
