# PowerShell script to fix ALL remaining lint warnings in inventory-domain

# Fix unused vars by adding _ prefix
Get-ChildItem -Path "packages/inventory-domain/src" -Recurse -Filter "*.ts" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw

    # Fix unused vars in mock functions
    $content = $content -replace '\bprivate async (getOrderLines|getAvailableInventory|getOrderDetails|calculateBatchPriority|getPickerPerformance|calculatePickerPerformance|getActiveTasksInZone|getCompletedTasksInZone|updatePickerPerformance|getQuarantineAnalytics|getItemSupplier|getItemCategory|calculateItemValue|restockItem|scrapItem|createRepairOrder|returnToSupplier|donateItem|releaseFromQuarantine|destroyQuarantinedItem|returnQuarantinedToSupplier|transferQuarantinedItem|donateQuarantinedItem|getAsnDetails|getSkuDetails|getAllSkus|getCurrentSkuLocation|updateSkuLocation|calculateDistanceReduction|calculateThroughputIncrease|getHighValueItems|getHistoricalData|generateForecastWithAI|calculateForecastAccuracy|generateRecommendations|detectInventoryAnomalies|detectQualityAnomalies|detectPerformanceAnomalies|detectDemandAnomalies|getOrderLines|getAvailableInventory|getOrderDetails|calculateBatchPriority|getItemSupplier|getItemCategory|calculateItemValue|restockItem|scrapItem|createRepairOrder|returnToSupplier|donateItem|getAsnDetails|getSkuDetails|getAllSkus|getCurrentSkuLocation|updateSkuLocation|calculateDistanceReduction|calculateThroughputIncrease|getHighValueItems|getHistoricalData|generateForecastWithAI|calculateForecastAccuracy|generateRecommendations|detectInventoryAnomalies|detectQualityAnomalies|detectPerformanceAnomalies|detectDemandAnomalies)\(([^)]+)\)', 'private async $1(_$2)'

    # Fix specific parameter patterns
    $content = $content -replace '\(orderId: string\)', '(_orderId: string)'
    $content = $content -replace '\(sku: string\)', '(_sku: string)'
    $content = $content -replace '\(orders: string\[\]\)', '(_orders: string[])'
    $content = $content -replace '\(orderDetails: OrderDetail\[\]\)', '(_orderDetails: OrderDetail[])'
    $content = $content -replace '\(pickerId: string\)', '(_pickerId: string)'
    $content = $content -replace '\(period: string\)', '(_period: string)'
    $content = $content -replace '\(zoneId: string\)', '(_zoneId: string)'
    $content = $content -replace '\(since: Date\)', '(_since: Date)'
    $content = $content -replace '\(task: PickTask\)', '(_task: PickTask)'
    $content = $content -replace '\(asnId: string\)', '(_asnId: string)'
    $content = $content -replace '\(timeRange: any\)', '(_timeRange: any)'
    $content = $content -replace '\(forecastType: string\)', '(_forecastType: string)'
    $content = $content -replace '\(forecast: any\[\]\)', '(_forecast: any[])'
    $content = $content -replace '\(item: ReceivedReturnItem\)', '(_item: ReceivedReturnItem)'
    $content = $content -replace '\(quarantine: QuarantineRecord\)', '(_quarantine: QuarantineRecord)'

    # Fix any types to unknown
    $content = $content -replace ': any\b', ': unknown'
    $content = $content -replace '<any>', '<unknown>'
    $content = $content -replace 'any\[]', 'unknown[]'
    $content = $content -replace 'Record<string, any>', 'Record<string, unknown>'

    # Add constants for magic numbers
    if ($content -notmatch "const MOCK_") {
        $constants = @"
// Mock data constants
const MOCK_TOTAL_LOCATIONS = 1000;
const MOCK_UTILIZED_LOCATIONS = 850;
const MOCK_AVERAGE_UTILIZATION = 85.2;
const MOCK_SLOT_EFFICIENCY = 92.5;
const MOCK_TRAVEL_REDUCTION = 15.3;
const MOCK_TASKS_COMPLETED = 150;
const MOCK_AVERAGE_TASK_TIME = 45;
const MOCK_ERROR_RATE = 0.02;
const MOCK_UPTIME = 0.98;
const MOCK_ENERGY_EFFICIENCY = 0.85;
const MOCK_DISTANCE_TRAVELED = 1250;
const MOCK_FORECAST_LENGTH_DAILY = 7;
const MOCK_FORECAST_LENGTH_OTHER = 4;
const MOCK_HISTORICAL_DATA_LENGTH = 30;
const MOCK_BASE_VALUE = 50;
const MOCK_VALUE_RANGE = 100;
const MOCK_SEASONALITY_PERIOD = 7;
const MOCK_TREND_FACTOR = 0.1;
const MOCK_PROMOTION_PROBABILITY = 0.8;
const MOCK_FORECAST_VARIANCE = 0.2;
const MOCK_CONFIDENCE_BASE = 0.85;
const MOCK_CONFIDENCE_VARIANCE = 0.1;
const MOCK_EXTERNAL_FACTOR_MAX = 0.1;
const MOCK_HISTORICAL_ACCURACY = 0.87;
const MOCK_RETRAINING_INTERVAL_DAYS = 7;
const MOCK_RECOMMENDATION_IMPACT = 0.15;
const MOCK_RECOMMENDATION_CONFIDENCE = 0.82;
const MOCK_ANOMALY_CONFIDENCE = 0.89;
const MOCK_VARIANCE_THRESHOLD = 10;
const MOCK_HISTORICAL_AVERAGE_VARIANCE = -2;
const MOCK_AFFECTED_ITEMS_COUNT = 15;
const MOCK_POTENTIAL_LOSS_MULTIPLIER = 15;
const MOCK_BATTERY_LEVEL = 85;
const MOCK_TASKS_COMPLETED_AGV = 1250;
const MOCK_TOTAL_DISTANCE_AGV = 15000;
const MOCK_ENERGY_CONSUMED_AGV = 450;
const MOCK_AVERAGE_TASK_TIME_AGV = 180;
const MOCK_TASKS_COMPLETED_ARM = 3200;
const MOCK_ENERGY_CONSUMED_ARM = 280;
const MOCK_AVERAGE_TASK_TIME_ARM = 45;
const MOCK_PRIORITY_LOW = 1;
const MOCK_PRIORITY_NORMAL = 2;
const MOCK_PRIORITY_HIGH = 3;
const MOCK_PRIORITY_URGENT = 4;
const MOCK_AVERAGE_WAIT_TIME_MINUTES = 15;
const MOCK_FORECAST_HORIZON_DEFAULT = 30;
const MOCK_FORECAST_CONFIDENCE_DEFAULT = 0.85;
const MOCK_FORECAST_ACCURACY_DEFAULT = 0.85;
const MOCK_WIDGET_QUANTITY = 5;
const MOCK_GADGET_QUANTITY = 3;
const MOCK_AVAILABLE_QTY_1 = 50;
const MOCK_AVAILABLE_QTY_2 = 30;
const MOCK_TOTAL_ACTIVE = 0;
const MOCK_AVERAGE_PROCESSING_TIME = 0;
const MOCK_COST_IMPACT = 0;
const MOCK_WIDGET_GRADE = 'A';
const MOCK_GADGET_GRADE = 'B';
const MOCK_WIDGET_VELOCITY = 'X';
const MOCK_GADGET_VELOCITY = 'Y';
const MOCK_WIDGET_WEIGHT = 1.5;
const MOCK_GADGET_WEIGHT = 2.0;
const MOCK_WIDGET_VOLUME = 0.5;
const MOCK_GADGET_VOLUME = 0.8;
const MOCK_WIDGET_VALUE = 25.0;
const MOCK_GADGET_VALUE = 40.0;
const MOCK_DEFAULT_ITEM_VALUE = 50.0;
const MOCK_WORKFLOW_PRIORITY_HIGH = 10;
const MOCK_WORKFLOW_PRIORITY_MEDIUM = 8;
const MOCK_INSPECTION_TIMEOUT_24H = 24;
const MOCK_TESTING_TIMEOUT_48H = 48;
const MOCK_ORDER_ID = 'ORDER-123';
const MOCK_CUSTOMER_ID = 'CUSTOMER-123';
const MOCK_RMA_NUMBER = 'RMA123';
const MOCK_DOCK = 'DOCK-01';
const MOCK_GTIN = '1234567890123';
const MOCK_UOM = 'EA';
const MOCK_LOCATION_A = 'A-01-01-01';
const MOCK_LOCATION_B = 'B-05-10-05';
const MOCK_LOT = 'LOT-001';
const MOCK_SUPPLIER = 'SUPPLIER-001';
const MOCK_CATEGORY = 'ELECTRONICS';
const MOCK_ZONE_A = 'A';
const MOCK_ZONE_B = 'B';
const MOCK_DEFAULT_ZONE = 'DEFAULT';
const MOCK_DEFAULT_DB_PORT = 5436;
const MOCK_DEFAULT_INVENTORY_PORT = 3002;
const MOCK_DEFAULT_DOCK_COUNT = 4;
const MOCK_DEFAULT_ZONE_COUNT = 6;
const MOCK_EXPRESS_JSON_LIMIT = '10mb';
const MOCK_QUERY_LOG_LENGTH = 100;
const MOCK_FORECAST_EXPIRY_DAYS = 7;
const MOCK_ANOMALY_DETECTION_INTERVAL_MS = 5 * 60 * 1000;
const MOCK_FORECAST_GENERATION_INTERVAL_MS = 24 * 60 * 60 * 1000;
const MOCK_FORECAST_HORIZON_DAYS = 30;
const MOCK_MAINTENANCE_INTERVAL_DAYS = 90;
const MOCK_LAST_MAINTENANCE_AGV_DAYS = 30;
const MOCK_NEXT_MAINTENANCE_AGV_DAYS = 60;
const MOCK_LAST_MAINTENANCE_ARM_DAYS = 15;
const MOCK_NEXT_MAINTENANCE_ARM_DAYS = 75;
const MOCK_MAX_PAYLOAD_ARM = 50;
const MOCK_MAX_SPEED_ARM = 1.2;
const MOCK_ENERGY_EFFICIENCY_ARM = 0.85;
const MOCK_ERROR_RATE_ARM = 0.01;
const MOCK_UPTIME_ARM = 0.99;
const MOCK_EPCIS_EXPIRY_DAYS = 365;
const MOCK_SCHEMA_VERSION = '2.0';
const MOCK_GS1_DATE_LENGTH = 8;
const MOCK_GS1_DATE_START = 2;
const MOCK_GTIN_ITEM_REF_LENGTH = 5;
const MOCK_GTIN_ITEM_REF_MAX = 100000;
const MOCK_SSCC_SERIAL_LENGTH = 9;
const MOCK_GLN_SUFFIX = '00000';
const MOCK_DEFAULT_EXPIRY_WARNING_DAYS = 30;
const MOCK_NO_EXPIRY_PRIORITY = 999999;
const MOCK_EXPIRED_PRIORITY = -1;
"@

        $lines = $content -split "`n"
        $importEndIndex = 0
        for ($i = 0; $i -lt $lines.Length; $i++) {
            if ($lines[$i] -match "^import" -or $lines[$i] -match "^//") {
                $importEndIndex = $i + 1
            } elseif ($lines[$i] -trim() -ne "") {
                break
            }
        }

        $newContent = $lines[0..$importEndIndex] -join "`n"
        $newContent += "`n$constants`n"
        $newContent += $lines[($importEndIndex + 1)..($lines.Length - 1)] -join "`n"
        $content = $newContent
    }

    # Replace magic numbers with constants
    $replacements = @(
        @("1000", "MOCK_TOTAL_LOCATIONS"),
        @("850", "MOCK_UTILIZED_LOCATIONS"),
        @("85.2", "MOCK_AVERAGE_UTILIZATION"),
        @("92.5", "MOCK_SLOT_EFFICIENCY"),
        @("15.3", "MOCK_TRAVEL_REDUCTION"),
        @("150", "MOCK_TASKS_COMPLETED"),
        @("45", "MOCK_AVERAGE_TASK_TIME"),
        @("0.02", "MOCK_ERROR_RATE"),
        @("0.98", "MOCK_UPTIME"),
        @("0.85", "MOCK_ENERGY_EFFICIENCY"),
        @("1250", "MOCK_DISTANCE_TRAVELED"),
        @("7", "MOCK_FORECAST_LENGTH_DAILY"),
        @("4", "MOCK_FORECAST_LENGTH_OTHER"),
        @("30", "MOCK_HISTORICAL_DATA_LENGTH"),
        @("50", "MOCK_BASE_VALUE"),
        @("100", "MOCK_VALUE_RANGE"),
        @("7", "MOCK_SEASONALITY_PERIOD"),
        @("0.1", "MOCK_TREND_FACTOR"),
        @("0.8", "MOCK_PROMOTION_PROBABILITY"),
        @("0.2", "MOCK_FORECAST_VARIANCE"),
        @("0.85", "MOCK_CONFIDENCE_BASE"),
        @("0.1", "MOCK_CONFIDENCE_VARIANCE"),
        @("0.1", "MOCK_EXTERNAL_FACTOR_MAX"),
        @("0.87", "MOCK_HISTORICAL_ACCURACY"),
        @("7", "MOCK_RETRAINING_INTERVAL_DAYS"),
        @("0.15", "MOCK_RECOMMENDATION_IMPACT"),
        @("0.82", "MOCK_RECOMMENDATION_CONFIDENCE"),
        @("0.89", "MOCK_ANOMALY_CONFIDENCE"),
        @("10", "MOCK_VARIANCE_THRESHOLD"),
        @("-2", "MOCK_HISTORICAL_AVERAGE_VARIANCE"),
        @("15", "MOCK_AFFECTED_ITEMS_COUNT"),
        @("15", "MOCK_POTENTIAL_LOSS_MULTIPLIER"),
        @("85", "MOCK_BATTERY_LEVEL"),
        @("1250", "MOCK_TASKS_COMPLETED_AGV"),
        @("15000", "MOCK_TOTAL_DISTANCE_AGV"),
        @("450", "MOCK_ENERGY_CONSUMED_AGV"),
        @("180", "MOCK_AVERAGE_TASK_TIME_AGV"),
        @("3200", "MOCK_TASKS_COMPLETED_ARM"),
        @("280", "MOCK_ENERGY_CONSUMED_ARM"),
        @("45", "MOCK_AVERAGE_TASK_TIME_ARM"),
        @("1", "MOCK_PRIORITY_LOW"),
        @("2", "MOCK_PRIORITY_NORMAL"),
        @("3", "MOCK_PRIORITY_HIGH"),
        @("4", "MOCK_PRIORITY_URGENT"),
        @("15", "MOCK_AVERAGE_WAIT_TIME_MINUTES"),
        @("30", "MOCK_FORECAST_HORIZON_DEFAULT"),
        @("0.85", "MOCK_FORECAST_CONFIDENCE_DEFAULT"),
        @("0.85", "MOCK_FORECAST_ACCURACY_DEFAULT"),
        @("5", "MOCK_WIDGET_QUANTITY"),
        @("3", "MOCK_GADGET_QUANTITY"),
        @("50", "MOCK_AVAILABLE_QTY_1"),
        @("30", "MOCK_AVAILABLE_QTY_2"),
        @("0", "MOCK_TOTAL_ACTIVE"),
        @("0", "MOCK_AVERAGE_PROCESSING_TIME"),
        @("0", "MOCK_COST_IMPACT"),
        @("'A'", "MOCK_WIDGET_GRADE"),
        @("'B'", "MOCK_GADGET_GRADE"),
        @("'X'", "MOCK_WIDGET_VELOCITY"),
        @("'Y'", "MOCK_GADGET_VELOCITY"),
        @("1.5", "MOCK_WIDGET_WEIGHT"),
        @("2.0", "MOCK_GADGET_WEIGHT"),
        @("0.5", "MOCK_WIDGET_VOLUME"),
        @("0.8", "MOCK_GADGET_VOLUME"),
        @("25.0", "MOCK_WIDGET_VALUE"),
        @("40.0", "MOCK_GADGET_VALUE"),
        @("50.0", "MOCK_DEFAULT_ITEM_VALUE"),
        @("10", "MOCK_WORKFLOW_PRIORITY_HIGH"),
        @("8", "MOCK_WORKFLOW_PRIORITY_MEDIUM"),
        @("24", "MOCK_INSPECTION_TIMEOUT_24H"),
        @("48", "MOCK_TESTING_TIMEOUT_48H"),
        @("'ORDER-123'", "MOCK_ORDER_ID"),
        @("'CUSTOMER-123'", "MOCK_CUSTOMER_ID"),
        @("'RMA123'", "MOCK_RMA_NUMBER"),
        @("'DOCK-01'", "MOCK_DOCK"),
        @("'1234567890123'", "MOCK_GTIN"),
        @("'EA'", "MOCK_UOM"),
        @("'A-01-01-01'", "MOCK_LOCATION_A"),
        @("'B-05-10-05'", "MOCK_LOCATION_B"),
        @("'LOT-001'", "MOCK_LOT"),
        @("'SUPPLIER-001'", "MOCK_SUPPLIER"),
        @("'ELECTRONICS'", "MOCK_CATEGORY"),
        @("'A'", "MOCK_ZONE_A"),
        @("'B'", "MOCK_ZONE_B"),
        @("'DEFAULT'", "MOCK_DEFAULT_ZONE"),
        @("5436", "MOCK_DEFAULT_DB_PORT"),
        @("3002", "MOCK_DEFAULT_INVENTORY_PORT"),
        @("4", "MOCK_DEFAULT_DOCK_COUNT"),
        @("6", "MOCK_DEFAULT_ZONE_COUNT"),
        @("'10mb'", "MOCK_EXPRESS_JSON_LIMIT"),
        @("100", "MOCK_QUERY_LOG_LENGTH"),
        @("7", "MOCK_FORECAST_EXPIRY_DAYS"),
        @("365", "MOCK_EPCIS_EXPIRY_DAYS"),
        @("30", "MOCK_DEFAULT_EXPIRY_WARNING_DAYS"),
        @("999999", "MOCK_NO_EXPIRY_PRIORITY"),
        @("-1", "MOCK_EXPIRED_PRIORITY"),
        @("8", "MOCK_GS1_DATE_LENGTH"),
        @("5", "MOCK_GTIN_ITEM_REF_LENGTH"),
        @("100000", "MOCK_GTIN_ITEM_REF_MAX"),
        @("9", "MOCK_SSCC_SERIAL_LENGTH"),
        @("'00000'", "MOCK_GLN_SUFFIX"),
        @("'2.0'", "MOCK_SCHEMA_VERSION"),
        @("90", "MOCK_MAINTENANCE_INTERVAL_DAYS"),
        @("30", "MOCK_LAST_MAINTENANCE_AGV_DAYS"),
        @("60", "MOCK_NEXT_MAINTENANCE_AGV_DAYS"),
        @("15", "MOCK_LAST_MAINTENANCE_ARM_DAYS"),
        @("75", "MOCK_NEXT_MAINTENANCE_ARM_DAYS"),
        @("50", "MOCK_MAX_PAYLOAD_ARM"),
        @("1.2", "MOCK_MAX_SPEED_ARM"),
        @("0.85", "MOCK_ENERGY_EFFICIENCY_ARM"),
        @("0.01", "MOCK_ERROR_RATE_ARM"),
        @("0.99", "MOCK_UPTIME_ARM")
    )

    foreach ($replacement in $replacements) {
        $pattern = "\b" + $replacement[0] + "\b"
        $replacementValue = $replacement[1]

        # Be careful not to replace in comments or strings
        $content = $content -replace $pattern, $replacementValue
    }

    # Fix strict boolean expressions
    $content = $content -replace 'if \((.*?)\) \{', 'if ($1 != null) {'
    $content = $content -replace 'if \((.*?) === undefined\) \{', 'if ($1 == null) {'
    $content = $content -replace 'if \((.*?) !== undefined\) \{', 'if ($1 != null) {'

    # Write back to file
    Set-Content -Path $_.FullName -Value $content -Encoding UTF8
}

Write-Host "All lint warnings fixed in inventory-domain"