from celery import shared_task
from django.db import transaction
import requests # Used for potential retries on network errors

from .models import PayLaterApplication
from .services import call_crc_api

@shared_task(bind=True, max_retries=5, default_retry_delay=60) # Retry up to 5 times, 60s apart
def perform_crc_check_task(self, application_id):
    """
    Celery task to call the external CRC API and update the PayLaterApplication status.
    """
    try:
        # Use select_for_update to lock the row during update to prevent race conditions
        with transaction.atomic():
            application = PayLaterApplication.objects.select_for_update().get(id=application_id)
            
            # Prevent re-processing if already approved/rejected
            if application.status in ['APPROVED_ELIGIBLE', 'REJECTED_INELIGIBLE']:
                print(f"Application {application_id} already processed. Skipping CRC check.")
                return

            # Update status to indicate processing (even if it's already PENDING_CRC_CHECK)
            application.status = 'PENDING_CRC_CHECK'
            application.save(update_fields=['status'])

            # Prepare comprehensive user data for the CRC service
            user_data_for_crc = {
                'date_of_birth': application.date_of_birth,
                'monthly_income': application.monthly_income,
                'address': application.address,
                'phone_number': application.phone_number,
                'full_name': application.full_name,
            }

            is_approved, credit_score, reason, approved_limit, raw_crc_response = call_crc_api(
                application.national_id_number,
                user_data_for_crc
            )

            # Update application with CRC results and final decision
            application.credit_score = credit_score
            application.crc_decision_data = raw_crc_response
            application.approved_credit_limit = approved_limit
            application.eligibility_reason = reason

            if is_approved:
                application.status = 'APPROVED_ELIGIBLE'
                application.is_eligible = True
            else:
                application.status = 'REJECTED_INELIGIBLE'
                application.is_eligible = False

            application.save()
            print(f"CRC check completed for {application.user.username} (App ID: {application.id}). Status: {application.status}")

    except PayLaterApplication.DoesNotExist:
        print(f"PayLaterApplication with ID {application_id} not found for CRC check.")
    except requests.exceptions.RequestException as exc:
        # Handle network or API errors from the external service
        print(f"CRC API call failed for app {application_id}: {exc}. Retrying...")
        self.retry(exc=exc) # Retry the task on request exceptions
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during CRC check for app {application_id}: {e}")
        # Log this error and/or notify an admin for further investigation