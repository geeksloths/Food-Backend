from django.db import models

from Utils.functions import get_uuid


class Address(models.Model):
    uuid = models.CharField(primary_key=True, max_length=15, unique=True, default=get_uuid, editable=False)
    title = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    latitude = models.TextField()
    longitude = models.TextField()
    brief_address = models.TextField()
    created_by = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.created_by + " " + self.brief_address
