import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalog_service.settings')
django.setup()

from django.db import connection

queries = [
    "ALTER TABLE products_category ADD COLUMN IF NOT EXISTS \"Title_en\" varchar(255);",
    "ALTER TABLE products_category ADD COLUMN IF NOT EXISTS \"Title_ar\" varchar(255);",
    "ALTER TABLE products_category ADD COLUMN IF NOT EXISTS \"Description_en\" text;",
    "ALTER TABLE products_category ADD COLUMN IF NOT EXISTS \"Description_ar\" text;",
    
    "ALTER TABLE products_matcategory ADD COLUMN IF NOT EXISTS \"Title_en\" varchar(255);",
    "ALTER TABLE products_matcategory ADD COLUMN IF NOT EXISTS \"Title_ar\" varchar(255);",
    
    "ALTER TABLE products_product ADD COLUMN IF NOT EXISTS \"ProductName_en\" varchar(100);",
    "ALTER TABLE products_product ADD COLUMN IF NOT EXISTS \"ProductName_ar\" varchar(100);",
    "ALTER TABLE products_product ADD COLUMN IF NOT EXISTS \"ProductDescription_en\" text;",
    "ALTER TABLE products_product ADD COLUMN IF NOT EXISTS \"ProductDescription_ar\" text;",
    
    "ALTER TABLE products_collection ADD COLUMN IF NOT EXISTS \"name_en\" varchar(100);",
    "ALTER TABLE products_collection ADD COLUMN IF NOT EXISTS \"name_ar\" varchar(100);"
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
print("Done adding translation columns.")
