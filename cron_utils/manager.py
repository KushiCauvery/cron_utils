from django.db import models

class MyAccountUsersManager(models.Manager):
    
    
    def deactivate_expired_users(self, active_duration, now):
        """
        when the user is expired due to time lapse of 30 days , it will be marked as deactivated using source as cron
        """
        return self.filter(is_activated_at__lte=active_duration, is_active=True
                           ).update(is_active=False, is_deactivated_at=now,
                                    deactivation_source='cron')
