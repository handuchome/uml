# 05. C4 Context Diagram

## 1. Diagram
```mermaid
C4Context
  title System Context - Bank Service Fee Collection System

  Person(staff, "Bank Staff", "Sử dụng hệ thống để tra cứu báo cáo (US-06)")
  System(feeSys, "Fee Collection System", "Hệ thống trung tâm xử lý thu phí dịch vụ tự động")

  System_Ext(digibank, "Digibank", "Nguồn dữ liệu (AppCode: DIGIBANK)")
  System_Ext(card, "Hệ thống Thẻ", "Nguồn dữ liệu (AppCode: CARD)")
  System_Ext(ibtc, "IB TC", "Nguồn dữ liệu (AppCode: IBTC)")
  System_Ext(params, "Hệ thống Params", "Cấu hình miễn giảm phí gốc")
  System_Ext(calendar, "Calendar API", "Cung cấp thông tin lịch Âm / Nghỉ lễ quốc gia")
  System_Ext(core, "Core Banking", "Quản lý tài khoản & Thực thi trích nợ")
  System_Ext(sms, "SMS Gateway", "Hệ thống gửi tin nhắn cho khách hàng")

  Rel(digibank, feeSys, "Gửi danh sách thu (US-01)")
  Rel(card, feeSys, "Gửi danh sách thu (US-01)")
  Rel(ibtc, feeSys, "Gửi danh sách thu (US-01)")

  Rel(feeSys, params, "Đồng bộ/Kiểm tra Params miễn giảm")
  Rel(feeSys, calendar, "Tra cứu mùng 1 Âm & Ngày lễ (BR-02)")
  Rel(feeSys, core, "Gửi lệnh trích nợ tài khoản (US-03)")
  Rel(feeSys, sms, "Gửi SMS ngay khi thu thành công (BR-04)")

  Rel(staff, feeSys, "Truy cập màn hình tra cứu")
```

## 2. Description
Hệ thống `Fee Collection System` đứng ở vị trí trung tâm, giao tiếp với các hệ thống nguồn để nhận dữ liệu, qua `Calendar API` để validate ngày hợp lệ, và thực thi các nghiệp vụ trừ tiền qua `Core Banking`.
