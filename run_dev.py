#!/usr/bin/env python
"""
Development server script with django-devsync
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def main():
    """Run development server with devsync"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    os.environ.setdefault('DEBUG', 'True')
    
    try:
        from django.core.management import execute_from_command_line
        from django.conf import settings
        
        # Check if devsync is enabled
        if hasattr(settings, 'DEVSYNC') and settings.DEVSYNC.get('ENABLED', False):
            print("🚀 Starting Django development server with DevSync...")
            print("📁 Watching directories:")
            for watch_dir in settings.DEVSYNC.get('WATCH_DIRS', []):
                print(f"   - {watch_dir}")
            print("🔄 Auto-reload enabled")
        else:
            print("🚀 Starting Django development server...")
        
        # Run the development server
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
        
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 