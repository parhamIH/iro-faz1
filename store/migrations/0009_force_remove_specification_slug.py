from django.db import migrations, connection

def force_remove_slug(apps, schema_editor):
    table_name = 'store_specification'
    column_name = 'slug'
    with connection.cursor() as cursor:
        # بررسی وجود ستون
        engine = connection.vendor
        if engine == 'sqlite':
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            if column_name in columns:
                try:
                    cursor.execute(f'ALTER TABLE {table_name} DROP COLUMN {column_name}')
                except Exception:
                    pass  # SQLite ممکن است DROP COLUMN را پشتیبانی نکند
        else:
            # برای PostgreSQL و MySQL
            try:
                cursor.execute(f'ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}')
            except Exception:
                pass

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0008_remove_specification_slug'),
    ]
    operations = [
        migrations.RunPython(force_remove_slug),
    ] 