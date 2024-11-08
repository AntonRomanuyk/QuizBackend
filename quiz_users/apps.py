from django.apps import AppConfig


class QuizUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz_users'

    def ready(self):
        import quiz_users.signals