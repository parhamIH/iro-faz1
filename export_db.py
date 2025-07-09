#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import *
from django.core.serializers import serialize

def export_database():
    """Export all database data to JSON format"""
    data = {}
    
    # Export all models
    models_to_export = [
        ('categories', Category),
        ('products', Product),
        ('specifications', Specification),
        ('product_specifications', ProductSpecification),
        ('brands', Brand),
        ('colors', Color),
        ('product_options', ProductOption),
        ('tags', Tag),
        ('warranties', Warranty),
        ('galleries', Gallery),
        ('article_categories', ArticleCategory),
        ('articles', Article),
    ]
    
    for name, model in models_to_export:
        try:
            objects = model.objects.all()
            data[name] = json.loads(serialize('json', objects))
            print(f"Exported {objects.count()} {name}")
        except Exception as e:
            print(f"Error exporting {name}: {e}")
            data[name] = []
    
    # Save to file
    with open('database_export.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nDatabase exported to database_export.json")
    print(f"Total data size: {len(json.dumps(data, ensure_ascii=False))} characters")

if __name__ == '__main__':
    export_database() 