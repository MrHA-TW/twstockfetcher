## Tasks for Feature: Query Stock Trading Information by Date Range

**Feature Branch**: `003-query-stock-data`

**Phase 1: Design & Contracts (已完成，但需審查/完善的任務)**
1.  [x] 審查 `spec.md` 和 `plan.md` 的完整性和清晰度。

**Phase 2: Task Planning (目前正在進行)**
2.  [x] 根據 `spec.md` 和 `plan.md` 產生 `tasks.md`。

**Phase 3: Implementation**

**Models:**
3.  **[P]** [x] 建立或更新 `src/models/stock_data.py`，定義股票交易資訊的資料模型，包括日期、開盤價、最高價、最低價、收盤價、成交量等欄位。

**CLI 參數處理與驗證:**
4.  [x] 為 `src/cli/main.py` 撰寫整合測試，驗證 `--stock`、`--start-date`、`--end-date` 參數的解析。
5.  [x] 在 `src/cli/main.py` 中實作參數解析，以接受 `--stock`、`--start-date`、`--end-date`。(FR-001, FR-002, FR-003)
6.  [x] 為 `src/cli/main.py` 撰寫整合測試，驗證日期格式驗證 (FR-005)。
7.  [x] 在 `src/cli/main.py` 中實作日期格式驗證 (FR-005)。
8.  [x] 為 `src/cli/main.py` 撰寫整合測試，驗證起始日期不晚於結束日期的驗證 (FR-006)。
9.  [x] 在 `src/cli/main.py` 中實作起始日期不晚於結束日期的驗證 (FR-006)。
10. [x] 為 `src/cli/main.py` 撰寫整合測試，驗證預設結束日期行為 (FR-008)。
11. [x] 在 `src/cli/main.py` 中實作預設結束日期邏輯 (FR-008)。
12. [x] 為 `src/cli/main.py` 撰寫整合測試，驗證無效股票代碼的處理 (FR-010)。
13. [x] 在 `src/cli/main.py` 中實作無效股票代碼的處理 (FR-010)。

**資料擷取服務:**
14. [x] 為 `src/services/data_fetcher.py` 撰寫整合測試，使用 `twstock` 或類似函式庫擷取指定股票代碼和日期範圍的股票資料。
15. [x] 在 `src/services/data_fetcher.py` 中實作資料擷取邏輯，從 `twstock` 擷取指定日期範圍的股票交易資訊 (FR-004)。

**資料庫服務:**
16. [x] 為 `src/services/db_service.py` 撰寫整合測試，儲存擷取的股票資料。
17. [x] 在 `src/services/db_service.py` 中實作儲存股票交易資訊的邏輯。
18. [x] 為 `src/services/db_service.py` 撰寫整合測試，擷取指定股票代碼和日期範圍的股票資料。
19. [x] 在 `src/services/db_service.py` 中實作擷取指定日期範圍的股票交易資訊的邏輯 (FR-004)。

**摘要/顯示服務:**
20. [x] 為 `src/services/summary_service.py` (或新服務) 撰寫整合測試，格式化並顯示查詢到的股票資料 (FR-007)。
21. [x] 在 `src/services/summary_service.py` (或新服務) 中實作格式化並顯示股票交易資訊的邏輯 (FR-007)。
22. [x] 為處理指定日期範圍內無資料的情況撰寫整合測試 (FR-009)。
23. [x] 實作處理指定日期範圍內無資料的情況 (FR-009)。

**整合與端到端測試:**
24. [x] 將 CLI 參數處理、資料擷取、資料庫互動和摘要顯示整合到 `src/cli/main.py` 中，以執行完整的查詢和顯示流程。
25. [x] 為整個 CLI 流程撰寫全面的端到端整合測試，涵蓋 `spec.md` 中的所有驗收情境。
