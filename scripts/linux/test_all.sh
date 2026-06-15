#!/bin/bash

echo "🚀 Starting test suite for all Django microservices..."

# List of Django services with tests
SERVICES=(
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
    echo "🧪 Running tests for $SERVICE..."
    docker compose exec $SERVICE python manage.py test
    
    if [ $? -eq 0 ]; then
        echo "✅ All tests passed for $SERVICE."
    else
        echo "❌ Tests failed for $SERVICE! Check the logs above."
        exit 1
    fi
done

echo "---------------------------------------------------------"
echo "🎉 All microservices passed their test suites!"
