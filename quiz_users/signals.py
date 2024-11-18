import logging

from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def log_user_update(sender, instance, created, **kwargs):
    if created:
        logger.info(f"User created: {instance.username}")
    else:
        logger.info(f"User updated: {instance.username}")


@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    logger.info(f"User deleted: {instance.username}")
