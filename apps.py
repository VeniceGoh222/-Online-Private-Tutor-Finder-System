from django.apps import AppConfig


class AdditemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'additem'

    def ready(self):
        import additem.signals  # Import signals here
