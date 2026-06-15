import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalog_service.settings')
django.setup()

from django.db import connection

queries = [
    "ALTER TABLE products_product RENAME COLUMN \"Supplier_id\" TO \"supplier_id\";",
    "ALTER TABLE products_product ADD COLUMN IF NOT EXISTS \"supplier_name\" varchar(255);",
    "ALTER TABLE products_product ADD COLUMN IF NOT EXISTS \"publish_status\" varchar(20) DEFAULT 'approved';"
]

cursor = connection.cursor()
for q in queries:
    print(f"Executing: {q}")
    try:
        cursor.execute(q)
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

connection.commit()
print("Done fixing products_product columns.")
