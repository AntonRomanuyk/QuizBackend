import logging

from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Company

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Company)
def log_company_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Company created: {instance.name} by {instance.owner.username}")
    else:
        logger.info(f"Company updated: {instance.name}")

@receiver(post_delete, sender=Company)
def log_company_delete(sender, instance, **kwargs):
    logger.info(f"Company deleted: {instance.name}")
