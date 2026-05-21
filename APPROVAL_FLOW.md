審核按鈕與流程說明

目的
- 為社長與指導老師提供在申請詳情頁直接同意的按鈕，並記錄審核事件。

實作檔案
- 視圖: `club/views.py`
  - `approve_sstu(request, pk)`：社長同意處理器。
  - `approve_sch(request, pk)`：指導老師（學校）同意處理器。
  - `_create_log(apply_obj, user_obj, club_obj, result=True, state=2)`：建立 `Log` 的 helper。
  - `Applyview.get_context_data()`：會注入 `logs` 至 template，供詳情頁顯示。
- 路由: `club/urls.py`
  - `path('<int:pk>/approve/sstu/', approve_sstu, name='approve_sstu')`
  - `path('<int:pk>/approve/sch/', approve_sch, name='approve_sch')`
- 模板: `templates/club/apply_detail.html`
  - 在「審核進度」區塊，若當前登入者為社長/指導老師且條件未通過，顯示可按的表單按鈕。
  - 按鈕透過 `POST` 發送至對應 handler，並包含 CSRF token。

權限檢查邏輯（簡述）
- `approve_sstu`：只允許 `us_rank == 1`（社長）且其 `club` 必須等於申請者的原社團（`apply.user.club`）。
- `approve_sch`：只允許 `us_rank == 2`（指導老師）且其 `club` 必須等於申請的目標社團（`apply.club`）。
- 若未登入或權限不符，會導向 `login` 或 `no_permission`。

其他注意事項與擴充建議
- 目前採用簡單布林欄位 `sstu_pass`、`sch_pass` 來表示審核結果；若未來需求進一步複雜（多階段、多人簽核），建議新增 `ApprovalLog` 模型或採用 `django-fsm` 狀態機。
- 建議加入 email 通知（使用 Celery）在每個審核通過時通知下一關審核者。
- 若需要「撤銷審核」或「不通過」功能，可新增對應 handler 並記錄 `Log.result=False`。

如何測試（手動）
1. 建立三個 `User`：學生(us_rank=0)、該學生原社團的社長(us_rank=1)、目標社團的指導老師(us_rank=2)，並建立兩個 `Club`。
2. 以學生身份登入並建立一筆 `Apply`。
3. 以原社團的社長登入到該申請詳情頁，應會看到「社長同意」按鈕，按下後 `sstu_pass` 會變為 `True` 並產生一筆 `Log`。
4. 以目標社團的指導老師登入並同理測試 `approve_sch`。

程式碼片段（參考）
- 模板按鈕（在 `apply_detail.html`）
  <form method="post" action="{% url 'approve_sstu' object.pk %}">{% csrf_token %}<button type="submit">社長同意</button></form>

- handler（在 `views.py`）
  def approve_sstu(request, pk):
      current_user = get_current_user(request)
      if current_user is None:
          return redirect('login')
      apply_obj = Apply.objects.get(pk=pk)
      if current_user.us_rank != 1 or current_user.club != apply_obj.user.club:
          return redirect('no_permission')
      if request.method == 'POST':
          apply_obj.sstu_pass = True
          apply_obj.save()
          _create_log(...)
      return redirect('apply_detail', pk=pk)

若你要我把說明加入 README 或轉成中文更詳細的開發文件，也可以幫你擴充。