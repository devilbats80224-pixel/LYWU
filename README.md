# iOS 離線網頁工具入口（PWA）

這個 repo 是你的 iOS 離線工具集合，目前入口頁 `index.html` 提供 7 個網頁工具可開啟（可加入 iPhone 主畫面使用）。

## 每個網頁是做什麼的

1. `gas-detector-app/index.single.html`  
   氣體偵測器與 CLPX 紙帶查詢，支援依氣體查詢與紙帶反查，含欄位設定、照片管理、JSON 匯入匯出備份。

2. `gas-leak-response-app/index.single.html`  
   氣體洩漏應變資料管理，支援應變內容查詢、照片/檔案管理與 JSON 匯入匯出備份。

3. `照片去背合成助手.html`  
   離線照片去背與合成工具，可做取樣色去背、筆刷修邊、光影融合與匯出成品圖。

4. `inspection-audit-app/index.single.html`  
   巡檢缺失稽核器：上傳 Excel 後設定分頁/欄位映射，執行交叉稽核並輸出結果摘要。

5. `f20-emergency-info-app/index.single.html`  
   F20 緊急應變資訊整合系統：以分頁方式集中查看與管理應變資訊。

6. `general-count-v4-app/index.single.html`  
   施工報表整理：施工報表資料編修、整理與匯入匯出。

7. `radiation-armband-v20-app/index.single.html`  
   輻射臂章檢點：臂章發放/繳回管理與紀錄查詢。

## 主要檔案

- `index.html`：iOS 離線 App 安裝入口（7 個工具連結）
- `serve_apps.sh`：本機啟動 HTTP Server，提供 iPhone Safari 安裝入口
- `build_apps.sh`：目前用於重建氣體相關兩個 App（`gas-detector-app`、`gas-leak-response-app`）

## iPhone 使用流程

1. 在 Mac 終端執行：

```bash
cd /Users/devil/Downloads/施工管制表/20260111/目前修改版/20260103/ios_offline_apps
./serve_apps.sh 8787
```

2. iPhone 與 Mac 連同一個 Wi-Fi。
3. iPhone Safari 開啟：`http://<你的Mac區網IP>:8787/`
4. 點進任一工具頁，按「分享」→「加入主畫面」。
5. 第一次開啟每個工具後停留 3-5 秒，讓離線快取完成。

## 備註

- 這些工具是單機離線網頁方案，不需 App Store 上架。
- 建議定期用各工具內建的 JSON 匯出做備份。
