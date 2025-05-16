class DBRouter:
    """
    Database Router for handling multiple databases in Django project
    روتر پایگاه داده برای مدیریت چندین دیتابیس در پروژه جنگو
    """
    
    def db_for_read(self, model, **hints):
        """
        Suggest the database that should be used for read operations for a given model
        پیشنهاد می‌دهد که کدام دیتابیس برای عملیات خواندن مدل مورد نظر استفاده شود
        """
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Suggest the database that should be used for write operations for a given model
        پیشنهاد می‌دهد که کدام دیتابیس برای عملیات نوشتن مدل مورد نظر استفاده شود
        """
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Determine if a relationship is allowed between two objects
        تعیین می‌کند که آیا رابطه بین دو شیء مجاز است یا خیر
        """
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Determine if the migration operation is allowed to run on the database
        تعیین می‌کند که آیا عملیات مایگریشن روی دیتابیس مجاز است یا خیر
        """
        return db == 'default'


        
    
