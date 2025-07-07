#!/usr/bin/env python
import json

# Load the exported data
with open('database_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== DATABASE SUMMARY ===")
for key, value in data.items():
    print(f"{key}: {len(value)} records")

print("\n=== SAMPLE DATA ===")
print("Categories:")
for cat in data['categories'][:3]:
    print(f"  - {cat['fields']['name']} (ID: {cat['pk']})")

print("\nProducts:")
for prod in data['products'][:3]:
    print(f"  - {prod['fields']['title']} (ID: {prod['pk']})")

print("\nSpecifications:")
for spec in data['specifications'][:3]:
    print(f"  - {spec['fields']['name']} (ID: {spec['pk']}, Type: {spec['fields']['data_type']})")

print("\nBrands:")
for brand in data['brands'][:3]:
    print(f"  - {brand['fields']['name']} (ID: {brand['pk']})")

print("\nColors:")
for color in data['colors'][:3]:
    print(f"  - {color['fields']['name']} (ID: {color['pk']})")

print(f"\nTotal data size: {len(json.dumps(data, ensure_ascii=False))} characters") 