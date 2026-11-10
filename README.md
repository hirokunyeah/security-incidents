# セキュリティインシデント台帳

国内外で公表された情報漏えい・不正アクセス・ランサムウェア等の事案を毎日集約した公開台帳です。

- 公開ページ: https://hirokunyeah.github.io/security-incidents/
- データ: `data/incidents.json`, `data/changelog.json`
- 毎朝の定期チェック（Claude）が最新データを Google ドライブに置き、GitHub Actions（`.github/workflows/update.yml`）がそれを取り込んでページを再生成します。
