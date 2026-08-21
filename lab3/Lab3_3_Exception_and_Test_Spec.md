# Lab 3: Exception and Test Spec

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 3

## 1. Exception Spec (G5 Evidence)

*Critical failure paths from CON.*: trigger, compensating action, who performs it.*

| Critical Failure Path (CON.*) | Trigger | Compensating Action | Who performs it (I-4 Container) |
|---|---|---|---|
| Chặn lịch (CON.2 - BR-02) | Calendar Service trả về trạng thái ngày nghỉ hoặc mùng 1 Âm lịch. | Tạm dừng luồng trích nợ, cập nhật trạng thái khoản thu thành `Rescheduled` để chờ xử lý vào ngày làm việc tiếp theo. | Calendar Gate / Execution Engine |
| Vượt quá giới hạn Retry (CON.3 - BR-03) | Lỗi số dư lặp lại nhiều lần khiến `RetryCount` đạt đến mức 10. | Ngừng chạy Retry, cập nhật trạng thái khoản thu thành `Failed_Permanently` để chặn vòng lặp vô hạn. | Retry Scheduler |

## 2. Test Spec (G6 Evidence)

*One row per I-6 transition and per sequence `alt`: ID, SUT (I-4 name), expected result.*

| Test ID | Mapped I-6 Transition / Sequence `alt` | SUT (System Under Test) | Expected Result |
|---|---|---|---|
| TC-01 | Created -> Pending_Calendar | Fee Processing Engine | Task được tạo thành công nếu phí > 0, sẵn sàng để check lịch. |
| TC-02 | `alt`: Phí <= 0 (Discard) | Fee Processing Engine | Task bị loại bỏ (discard), không ghi nhận vào hệ thống. |
| TC-03 | Pending_Calendar -> Pending_Execution | Calendar Gate | Request được thông qua, trạng thái chuyển thành Pending_Execution. |
| TC-04 | Pending_Calendar -> Rescheduled | Calendar Gate | Request bị chặn, task chuyển sang Rescheduled (Lễ/Mùng 1 Âm). |
| TC-05 | `alt`: Ngày Lễ (Reschedule) | Execution Engine | Luồng trích nợ dừng lại, không gọi Core Banking. |
| TC-06 | Rescheduled -> Pending_Calendar | Retry Scheduler | Khi đến ngày làm việc tiếp theo, task được kích hoạt lại vòng đời. |
| TC-07 | Pending_Execution -> Completed | Execution Engine | Trích nợ Core thành công, cập nhật trạng thái Completed và kích hoạt SMS. |
| TC-08 | Pending_Execution -> Retrying | Execution Engine | Lỗi số dư, `RetryCount` tăng lên 1, trạng thái thành Retrying. |
| TC-09 | `alt`: Lỗi số dư (To Retry) | Execution Engine | Bắt đúng mã lỗi số dư từ Core để kích hoạt luồng Retry, không ném exception hệ thống. |
| TC-10 | Retrying -> Pending_Execution | Retry Scheduler | `RetryCount` < 10, task được gửi lại Execution Engine để thử lại. |
| TC-11 | Retrying -> Failed_Permanently | Retry Scheduler | `RetryCount` = 10, trạng thái chốt hạ là Failed_Permanently. |
| TC-12 | `alt`: Vượt quá 10 lần (Fail) | Retry Scheduler | Không phát sinh thêm bất kỳ lệnh gọi Core Banking nào sau lần thứ 10. |
