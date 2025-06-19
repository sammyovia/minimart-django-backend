from rest_framework import serializers
from .models import PayLaterApplication

class PayLaterApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayLaterApplication
        fields = [
            'id', 'user', 'status', 'full_name', 'national_id_number',
            'date_of_birth', 'address', 'phone_number', 'employment_status',
            'monthly_income', 'credit_score', 'crc_decision_data',
            'is_eligible', 'eligibility_reason', 'approved_credit_limit',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'status', 'credit_score', 'crc_decision_data',
            'is_eligible', 'eligibility_reason', 'approved_credit_limit',
            'created_at', 'updated_at'
        ]
        # Make these fields writable for initial submission,
        # but read-only for subsequent checks. The `create` method handles `user` and `status`.

    def create(self, validated_data):
        user = self.context['request'].user
        if PayLaterApplication.objects.filter(user=user).exists():
            raise serializers.ValidationError("A Pay Later application already exists for this user.")
        
        validated_data['user'] = user
        validated_data['status'] = 'SUBMITTED_KYC' # Initial status after user submission
        return super().create(validated_data)

class PayLaterEligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayLaterApplication
        fields = ['is_eligible', 'status', 'eligibility_reason', 'approved_credit_limit']
        read_only_fields = ['is_eligible', 'status', 'eligibility_reason', 'approved_credit_limit']