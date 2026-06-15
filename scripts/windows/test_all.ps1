Write-Host "🚀 Starting test suite for all Django microservices..." -ForegroundColor Cyan

$SERVICES = @(
    "auth_service",
    "catalog_service",
    "order_service",
    "payment_service",
    "platform_service",
    "reporting_service"
)

foreach ($SERVICE in $SERVICES) {
    Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "🧪 Running tests for $SERVICE..." -ForegroundColor Yellow
    
    docker compose exec $SERVICE python manage.py test
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All tests passed for $SERVICE." -ForegroundColor Green
    } else {
        Write-Host "❌ Tests failed for $SERVICE! Check the logs above." -ForegroundColor Red
        exit 1
    }
}

Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "🎉 All microservices passed their test suites!" -ForegroundColor Green
