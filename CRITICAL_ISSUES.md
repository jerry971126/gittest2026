重要問題（只列出會大幅影響專案運作的項目）

1) DEBUG 與 SECRET_KEY（安全性、重大）
- 問題：`form/settings.py` 設定 `DEBUG = True` 且 `SECRET_KEY` 直接寫在檔案中。
- 影響：生產環境會洩漏詳細錯誤與敏感資訊。
- 建議：在生產將 `DEBUG=False`，並把 `SECRET_KEY` 與其他敏感設定移到環境變數或 secrets 管理系統。
- 檔案：`form/settings.py`

2) 靜態檔案放在 `templates/`（功能性錯誤、重大）
- 問題：`css.css` 與 `javascripts.js` 現在放在 `templates/`，同時 `STATICFILES_DIRS` 指向 `templates`。
- 影響：靜態檔案不會按預期被 Django collectstatic 處理，部署或本地伺服器可能找不到 CSS/JS，導致 UI 毀損。
- 建議：建立 `static/`（例如 `static/css/`, `static/js/`），移動相關檔案，更新 `settings.py`（`STATICFILES_DIRS`）與模板中 `{% static %}` 的引用。
- 檔案：`templates/css.css`, `templates/javascripts.js`, `form/settings.py`

3) 重複/錯誤的資料庫檔案（高影響）
- 問題：專案根目錄與 `form/` 內存在兩個 `db.sqlite3`。
- 影響：開發或部署時可能連到不同資料庫，造成資料不一致、遷移錯誤與難以追蹤 bug。
- 建議：保留單一資料庫路徑（通常根目錄的 `db.sqlite3`），備份並刪除多餘檔案，並確認 `DATABASES['default']['NAME']` 指向正確路徑。
- 檔案：`/db.sqlite3`, `form/db.sqlite3`, `form/settings.py`

4) `club/views.py` 中的錯誤 `select_related` 語法（會直接造成程式錯誤）
- 問題：`Log.objects.select_related('club__club_name')` 用法錯誤（`select_related` 接關聯欄位名稱，如 `'club'`）。
- 影響：視圖可能拋出例外或失去效能優化，導致頁面 500 錯誤。
- 建議：改為 `select_related('club')` 或移除錯誤用法，並在必要處加入 `.prefetch_related()`。
- 檔案：`club/views.py`

5) 模型設計可能造成資料不一致（`Log` 冗餘 FK）
- 問題：`Log` 模型同時儲存 `apply`, `user`, `club`，而 `apply` 已關聯 `user` 與 `club`。
- 影響：若不同步更新，會導致資料不一致，影響審核邏輯與報表正確性。
- 建議：重新設計 `Log`，只關聯 `Apply`（必要時透過 `Apply` 取得 `user` 與 `club`），或在建立 `Log` 時嚴格同步欄位。
- 檔案：`club/models.py`

6) 表單直接使用 `fields='__all__'`（資料驗證與安全風險）
- 問題：`CreateView` 使用 `fields='__all__'`，缺少欄位限制與自訂驗證。
- 影響：使用者可能送出不預期或惡意資料，造成資料庫不一致或安全風險。
- 建議：改為使用 `ModelForm`，只暴露必要欄位並加入驗證（例如 email 格式、唯一性檢查）。
- 檔案：`club/views.py`, `templates/*_form.html`

7) 管理後台未註冊模型（影響管理與除錯）
- 問題：`club/admin.py` 尚未註冊模型。
- 影響：管理員無法透過 admin 檢視或編輯資料，降低維運效率。
- 建議：在 `admin.py` 註冊 `Club`, `User`, `Apply`, `Log`。
- 檔案：`club/admin.py`

---

我已把上述重要項目寫入 `CRITICAL_ISSUES.md`。要我接著自動修第 1、2、3 項（安全設定、靜態檔重構、資料庫合併），還是先產出簡單的修正 PR 列表？
