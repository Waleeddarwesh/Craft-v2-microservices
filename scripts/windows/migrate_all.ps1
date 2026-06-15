Write-Host "🚀 Starting database migrations for all Django microservices..." -ForegroundColor Cyan

$SERVICES = @(
    "admin_service",
    "auth_service",
    "catalog_service",
    "order_service",
    "payment_service",
    "platform_service",
    "reporting_service"
)

foreach ($SERVICE in $SERVICES) {
    Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "🔄 Migrating $SERVICE..." -ForegroundColor Yellow
    
    docker compose exec $SERVICE python manage.py migrate
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully migrated $SERVICE." -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to migrate $SERVICE! Check the logs above." -ForegroundColor Red
    }
}

Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "🎉 All migrations completed!" -ForegroundColor Green
