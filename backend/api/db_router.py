"""
数据库路由器 - 多数据库配置
实现 Ralendar 的部分共享架构
"""


class RalendarRouter:
    """
    数据库路由器：将不同的模型路由到不同的数据库
    
    架构：
    - default (roamio_production): 用户、OAuth 等共享数据
    - ralendar (ralendar_production): Ralendar 特有数据（事件、节假日、黄历、运势）
    """
    
    # Ralendar 独立数据库的应用
    ralendar_apps = {'api'}
    
    # Ralendar 独立数据库的模型
    ralendar_models = {
        'event',              # 事件
        'publiccalendar',     # 公共日历
        'holiday',            # 节假日
        'lunarcalendar',      # 黄历
        'dailyfortune',       # 运势
        'userfortune',        # 用户运势配置
        'datasynclog',        # 数据同步日志
    }
    
    # 共享数据库的模型（与 Roamio 共享）
    shared_models = {
        'user',               # Django 用户
        'group',              # Django 用户组
        'permission',         # Django 权限
        'contenttype',        # Django ContentType
        'session',            # Django Session
        'socialaccount',      # allauth - OAuth 账号
        'socialapp',          # allauth - OAuth 应用
        'socialtoken',        # allauth - OAuth Token
        'acwinguser',         # AcWing 用户
        'qquser',             # QQ 用户
        'usermapping',        # Roamio-Ralendar 用户映射
    }
    
    def db_for_read(self, model, **hints):
        """
        读取操作：确定使用哪个数据库
        """
        model_name = model._meta.model_name.lower()
        
        # Ralendar 独立数据：使用 ralendar 数据库
        if model_name in self.ralendar_models:
            return 'ralendar'
        
        # 共享数据：使用 default 数据库
        if model_name in self.shared_models:
            return 'default'
        
        # 默认：使用 default 数据库
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        写入操作：确定使用哪个数据库
        """
        model_name = model._meta.model_name.lower()
        
        # Ralendar 独立数据：使用 ralendar 数据库
        if model_name in self.ralendar_models:
            return 'ralendar'
        
        # 共享数据：使用 default 数据库
        if model_name in self.shared_models:
            return 'default'
        
        # 默认：使用 default 数据库
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        是否允许两个对象之间的关联
        """
        model1_name = obj1._meta.model_name.lower()
        model2_name = obj2._meta.model_name.lower()
        
        # 同一数据库内的关联：允许
        if model1_name in self.ralendar_models and model2_name in self.ralendar_models:
            return True
        if model1_name in self.shared_models and model2_name in self.shared_models:
            return True
        
        # 跨数据库关联（Ralendar ↔ Shared）：允许
        # 例如：Event.user (ralendar) → User (shared)
        if (model1_name in self.ralendar_models and model2_name in self.shared_models) or \
           (model1_name in self.shared_models and model2_name in self.ralendar_models):
            return True
        
        # 其他情况：默认允许
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        是否允许在指定数据库上执行迁移
        """
        if model_name:
            model_name_lower = model_name.lower()
            
            # Ralendar 独立数据：只在 ralendar 数据库迁移
            if model_name_lower in self.ralendar_models:
                return db == 'ralendar'
            
            # 共享数据：只在 default 数据库迁移
            if model_name_lower in self.shared_models:
                return db == 'default'
        
        # Django 内置应用：只在 default 数据库迁移
        if app_label in ['auth', 'contenttypes', 'sessions', 'admin', 'allauth', 'socialaccount']:
            return db == 'default'
        
        # api 应用：根据模型决定
        if app_label == 'api':
            if model_name and model_name.lower() in self.ralendar_models:
                return db == 'ralendar'
            else:
                return db == 'default'
        
        # 其他应用：默认在 default 数据库
        return db == 'default'

