from rest_framework import serializers
from .models import LoanCondition

class LoanConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanCondition
        fields = '__all__'
