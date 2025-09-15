from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    hr_created_by = serializers.SerializerMethodField()
    hr_updated_by = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['updated_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['updated_by'] = user
        validated_data.pop('created_by', None)
        return super().update(instance, validated_data)

    def get_hr_created_by(self, obj):
        return str(obj.created_by) if obj.created_by else None

    def get_hr_updated_by(self, obj):
        return str(obj.updated_by) if obj.updated_by else None