import json

from typing import Dict, Any, Iterable, Union

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Max, Min, Prefetch
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers

from . import models

class ActivityLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.Log
        fields=("action", "description", "timestamp")