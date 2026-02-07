# 兩個獨立 iOS 離線 App（PWA 版）

已建立兩個可獨立加入 iPhone 主畫面的離線 App：

- `gas-detector-app`（氣體偵測器查詢）
- `gas-leak-response-app`（氣體洩漏應變）

## 目錄

- `build_apps.sh`：每次原始 HTML 更新後，重建兩個 App 的 `index.html`
- `serve_apps.sh`：本機啟動 HTTP Server，給 iPhone Safari 安裝
- `index.html`：安裝入口頁（含兩個 App 連結）

## 一次安裝流程（自己手機用）

1. 在 Mac 終端執行：

```bash
cd /Users/devil/Downloads/施工管制表/20260111/目前修改版/20260103/ios_offline_apps
./build_apps.sh
./serve_apps.sh 8787
```

2. iPhone 與 Mac 連同一個 Wi-Fi。
3. iPhone Safari 開啟：`http://<你的Mac區網IP>:8787/`
4. 先點進第一個 App 頁面，按「分享」→「加入主畫面」。
5. 回到入口頁，再點進第二個 App，重複加入主畫面。
6. 每個 App 第一次開啟後先停留 3-5 秒，讓離線快取完成。
7. 開飛航模式測試：兩個 App 可直接開啟。

## 更新內容後如何同步

只要原始檔有修改：

```bash
cd /Users/devil/Downloads/施工管制表/20260111/目前修改版/20260103/ios_offline_apps
./build_apps.sh
./serve_apps.sh 8787
```

然後在 iPhone 重新開啟 App，離線快取會更新。

## 注意事項

- 這是 iOS「主畫面 Web App（PWA）」方案，無需 App Store、無需上架。
- 完全離線可用，但 iOS 仍可能在系統儲存空間不足時清理網站資料。
- 建議定期用你網頁內建的 JSON 匯出功能備份資料。
