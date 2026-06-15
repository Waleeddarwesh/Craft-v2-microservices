#!/bin/bash

echo "🚀 Starting database migrations for all Django microservices..."

# List of all Django services
SERVICES=(
    "admin_service"
    "auth_service"
    "catalog_service"
    "order_service"
    "payment_service"
    "platform_service"
    "reporting_service"
)

for SERVICE in "${SERVICES[@]}"
do
    echo "---------------------------------------------------------"
    echo "🔄 Migrating $SERVICE..."
    docker compose exec $SERVICE python manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully migrated $SERVICE."
    else
        echo "❌ Failed to migrate $SERVICE! Check the logs above."
    fi
done

echo "---------------------------------------------------------"
echo "🎉 All migrations completed!"
