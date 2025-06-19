from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PayLaterApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING_SUBMISSION', 'Pending Submission'),
        ('SUBMITTED_KYC', 'KYC Submitted'),
        ('PENDING_CRC_CHECK', 'Pending Credit Check'),
        ('CRC_APPROVED', 'Credit Check Approved'),
        ('CRC_REJECTED', 'Credit Check Rejected'),
        ('APPROVED_ELIGIBLE', 'Approved for Pay Later'),
        ('REJECTED_INELIGIBLE', 'Rejected for Pay Later'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pay_later_application',
                                help_text="The user submitting this application.")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING_SUBMISSION',
                              help_text="Current status of the Pay Later application.")

    # KYC Details (adjust to actual CRC/KYC requirements for your region)
    full_name = models.CharField(max_length=255)
    national_id_number = models.CharField(max_length=50, unique=True,
                                          help_text="e.g., NIN, Driver's License number, Passport number.")
    date_of_birth = models.DateField()
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    employment_status = models.CharField(max_length=100, blank=True, null=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Details from CRC/Credit Check (Populated by backend after external call)
    credit_score = models.IntegerField(null=True, blank=True,
                                       help_text="Credit score returned by CRC software.")
    crc_decision_data = models.JSONField(null=True, blank=True,
                                         help_text="Raw JSON response from CRC software for auditing.")
    approved_credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                                help_text="Maximum credit limit approved by CRC/system.")

    # Final Eligibility Decision
    is_eligible = models.BooleanField(default=False,
                                      help_text="Final decision on user's Pay Later eligibility.")
    eligibility_reason = models.TextField(blank=True, null=True,
                                         help_text="Reason for approval or rejection.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pay Later App for {self.user.username} - {self.status}"

    class Meta:
        verbose_name_plural = "Pay Later Applications"