from rest_framework import serializers

from main.models import Plan


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'
