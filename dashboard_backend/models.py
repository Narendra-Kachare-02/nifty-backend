from django.db import models
from django.utils import timezone
from .managers import SoftDeleteManager

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    all_objects = models.Manager()
    objects = SoftDeleteManager()

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True
    
