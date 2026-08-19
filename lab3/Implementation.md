# Implementation - Bank Service Fee Collection System

**Language:** Java 17+ / Spring Boot
**Architecture:** Dựa trên [Architecture.md] và [Detailed-Design.md]

## 1. Domain Models & Enums

```java
package com.bank.fee.domain;

import java.math.BigDecimal;
import java.time.LocalDate;

public enum TaskStatus {
    PENDING, SUCCESS, INSUFFICIENT_FUNDS, PERMANENT_FAIL, RESCHEDULED
}

public class RawFeeRecord {
    private String appCode;
    private String maKhachHang;
    private BigDecimal soTienGoc;
    
    // Getters, Setters, Constructors
    public String getAppCode() { return appCode; }
    public String getMaKhachHang() { return maKhachHang; }
    public BigDecimal getSoTienGoc() { return soTienGoc; }
}

public class ProcessedFeeTask {
    private String taskId;
    private String loaiPhi;
    private BigDecimal soTienPhi;
    private int retryCount;
    private TaskStatus status;
    private LocalDate ngayPhaiThu;
    private String maKhachHang;

    // Getters, Setters
    public BigDecimal getSoTienPhi() { return soTienPhi; }
    public int getRetryCount() { return retryCount; }
    public void setRetryCount(int retryCount) { this.retryCount = retryCount; }
    public TaskStatus getStatus() { return status; }
    public void setStatus(TaskStatus status) { this.status = status; }
    public LocalDate getNgayPhaiThu() { return ngayPhaiThu; }
    public void setNgayPhaiThu(LocalDate ngayPhaiThu) { this.ngayPhaiThu = ngayPhaiThu; }
    public String getMaKhachHang() { return maKhachHang; }
}
```

## 2. Ingestion Service (US-01, BR-01)

```java
package com.bank.fee.service;

import com.bank.fee.domain.*;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.List;

@Service
public class IngestionService {
    
    private final ParamsClient paramsClient;
    private final FeeTaskRepository repository;

    public IngestionService(ParamsClient paramsClient, FeeTaskRepository repository) {
        this.paramsClient = paramsClient;
        this.repository = repository;
    }

    public void processRawRecords(List<RawFeeRecord> records) {
        for (RawFeeRecord record : records) {
            BigDecimal actualFee = paramsClient.applyDiscount(record);
            
            // BR-01: Chỉ thu khoản có Số tiền > 0
            if (actualFee != null && actualFee.compareTo(BigDecimal.ZERO) > 0) {
                ProcessedFeeTask task = new ProcessedFeeTask();
                task.setSoTienPhi(actualFee);
                task.setStatus(TaskStatus.PENDING);
                task.setRetryCount(0);
                task.setMaKhachHang(record.getMaKhachHang());
                repository.save(task);
            }
        }
    }
}
```

## 3. Calendar Gate (US-02, BR-02)

```java
package com.bank.fee.service;

import org.springframework.stereotype.Component;
import java.time.LocalDate;

@Component
public class CalendarGate {
    
    private final CalendarApiClient calendarApi;

    public CalendarGate(CalendarApiClient calendarApi) {
        this.calendarApi = calendarApi;
    }

    // BR-02: Chặn mùng 1 Âm lịch và Nghỉ lễ
    public boolean canExecute(LocalDate date) {
        CalendarInfo info = calendarApi.getDateInfo(date);
        return !info.isLunarFirst() && !info.isHoliday();
    }
}
```

## 4. Execution Engine & SMS (US-03, US-05, BR-04)

```java
package com.bank.fee.service;

import com.bank.fee.domain.*;
import org.springframework.stereotype.Service;
import java.time.LocalDate;

@Service
public class ExecutionEngine {

    private final CalendarGate calendarGate;
    private final CoreBankingClient coreBanking;
    private final SmsGatewayClient smsGateway;
    private final FeeTaskRepository repository;

    public ExecutionEngine(CalendarGate calendarGate, CoreBankingClient coreBanking, 
                           SmsGatewayClient smsGateway, FeeTaskRepository repository) {
        this.calendarGate = calendarGate;
        this.coreBanking = coreBanking;
        this.smsGateway = smsGateway;
        this.repository = repository;
    }

    public void executeTask(ProcessedFeeTask task) {
        // Validation qua Calendar Gate trước khi gọi Core
        if (!calendarGate.canExecute(task.getNgayPhaiThu())) {
            task.setStatus(TaskStatus.RESCHEDULED);
            task.setNgayPhaiThu(task.getNgayPhaiThu().plusDays(1)); // Dời lịch ngày làm việc tiếp theo
            repository.save(task);
            return;
        }

        CoreResponse response = coreBanking.chargeFee(task.getMaKhachHang(), task.getSoTienPhi());

        if (response.isSuccess()) {
            task.setStatus(TaskStatus.SUCCESS);
            // BR-04: Thu thành công bắt buộc trigger SMS ngay lập tức
            smsGateway.sendSms(task.getMaKhachHang(), "Trích nợ thành công số tiền: " + task.getSoTienPhi());
        } else if (response.isInsufficientFunds()) {
            handleRetry(task);
        }
        
        repository.save(task);
    }

    // BR-03: AutoRetry tối đa 10 lần
    private void handleRetry(ProcessedFeeTask task) {
        if (task.getRetryCount() < 10) {
            task.setRetryCount(task.getRetryCount() + 1);
            task.setStatus(TaskStatus.INSUFFICIENT_FUNDS);
        } else {
            task.setStatus(TaskStatus.PERMANENT_FAIL);
        }
    }
}
```

## 5. Retry Scheduler (US-04, BR-03)

```java
package com.bank.fee.scheduler;

import com.bank.fee.domain.*;
import com.bank.fee.service.ExecutionEngine;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import java.util.List;

@Component
public class RetryScheduler {

    private final FeeTaskRepository repository;
    private final ExecutionEngine executionEngine;

    public RetryScheduler(FeeTaskRepository repository, ExecutionEngine executionEngine) {
        this.repository = repository;
        this.executionEngine = executionEngine;
    }

    @Scheduled(cron = "0 0 * * * *") // Chạy mỗi giờ
    public void processRetries() {
        // Tìm các task đang lỗi số dư và chưa vượt quá 10 lần retry
        List<ProcessedFeeTask> tasks = repository.findByStatusAndRetryCountLessThan(
            TaskStatus.INSUFFICIENT_FUNDS, 10
        );
        
        for (ProcessedFeeTask task : tasks) {
            executionEngine.executeTask(task);
        }
    }
}
```
