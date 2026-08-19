# Tests - Bank Service Fee Collection System

**Framework:** JUnit 5, Mockito
**Mục tiêu:** Verify 100% các Business Rules (BR-01 đến BR-04) theo [Detailed-Design.md]

```java
package com.bank.fee.service;

import com.bank.fee.domain.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Collections;

class BankServiceFeeTests {

    private ParamsClient paramsClient;
    private FeeTaskRepository repository;
    private CalendarApiClient calendarApi;
    private CoreBankingClient coreBanking;
    private SmsGatewayClient smsGateway;

    private IngestionService ingestionService;
    private CalendarGate calendarGate;
    private ExecutionEngine executionEngine;

    @BeforeEach
    void setUp() {
        paramsClient = mock(ParamsClient.class);
        repository = mock(FeeTaskRepository.class);
        calendarApi = mock(CalendarApiClient.class);
        coreBanking = mock(CoreBankingClient.class);
        smsGateway = mock(SmsGatewayClient.class);

        ingestionService = new IngestionService(paramsClient, repository);
        calendarGate = new CalendarGate(calendarApi);
        executionEngine = new ExecutionEngine(calendarGate, coreBanking, smsGateway, repository);
    }

    @Test
    void testBR01_ShouldOnlyProcessFeeGreaterThanZero() {
        // Given
        RawFeeRecord record = new RawFeeRecord();
        when(paramsClient.applyDiscount(record)).thenReturn(BigDecimal.ZERO); // Phí = 0

        // When
        ingestionService.processRawRecords(Collections.singletonList(record));

        // Then
        verify(repository, never()).save(any(ProcessedFeeTask.class)); // Không lưu task
    }

    @Test
    void testBR02_ShouldHaltExecutionOnLunarFirstOrHoliday() {
        // Given
        ProcessedFeeTask task = new ProcessedFeeTask();
        LocalDate today = LocalDate.now();
        task.setNgayPhaiThu(today);
        
        CalendarInfo blockInfo = new CalendarInfo(true, false); // Mùng 1 Âm
        when(calendarApi.getDateInfo(today)).thenReturn(blockInfo);

        // When
        executionEngine.executeTask(task);

        // Then
        assertEquals(TaskStatus.RESCHEDULED, task.getStatus());
        verify(coreBanking, never()).chargeFee(any(), any()); // TUYỆT ĐỐI KHÔNG gọi Core
    }

    @Test
    void testBR04_ShouldSendSmsImmediatelyOnSuccess() {
        // Given
        ProcessedFeeTask task = new ProcessedFeeTask();
        task.setNgayPhaiThu(LocalDate.now());
        task.setSoTienPhi(new BigDecimal("55000"));
        
        when(calendarApi.getDateInfo(any())).thenReturn(new CalendarInfo(false, false));
        CoreResponse successResponse = new CoreResponse(true, false);
        when(coreBanking.chargeFee(any(), any())).thenReturn(successResponse);

        // When
        executionEngine.executeTask(task);

        // Then
        assertEquals(TaskStatus.SUCCESS, task.getStatus());
        verify(smsGateway, times(1)).sendSms(any(), contains("55000")); // SMS được trigger
    }

    @Test
    void testBR03_ShouldIncrementRetryAndHaltAt10() {
        // Given
        ProcessedFeeTask task = new ProcessedFeeTask();
        task.setNgayPhaiThu(LocalDate.now());
        task.setRetryCount(9); // Đã retry 9 lần
        
        when(calendarApi.getDateInfo(any())).thenReturn(new CalendarInfo(false, false));
        CoreResponse failResponse = new CoreResponse(false, true); // Lỗi số dư
        when(coreBanking.chargeFee(any(), any())).thenReturn(failResponse);

        // When - Lần 10
        executionEngine.executeTask(task);

        // Then
        assertEquals(10, task.getRetryCount());
        assertEquals(TaskStatus.INSUFFICIENT_FUNDS, task.getStatus());

        // When - Vượt quá lần 10
        executionEngine.executeTask(task);

        // Then
        assertEquals(TaskStatus.PERMANENT_FAIL, task.getStatus()); // Đánh dấu thất bại vĩnh viễn
    }
}
```
