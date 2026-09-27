# pocamaster

IVE のフォトカード収集を管理する、自分用の iPhone 向け PWA。

- 設計資料：[docs/](docs/)
- データは iPhone の中（IndexedDB）にだけ保存する

## 開発

```bash
npm install
npm run dev
```

ブラウザで http://localhost:5173/pocamaster/ を開く。

## 公開

`main` ブランチに push すると、GitHub Actions が GitHub Pages に公開する。

## 初期データ

`public/seed/collections.csv` と `public/seed/cards.csv`。アプリの「設定 → 初期データを取り込む」で読み込む。
