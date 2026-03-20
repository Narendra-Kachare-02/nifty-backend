from django.apps import AppConfig


class NiftyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard_backend.nifty"

    def ready(self) -> None:
        # Start in-process scheduler only when running the Django web server.
        # See `scheduler.py` for the exact gating/lock behavior.
        from .scheduler import start_nifty_scheduler

        start_nifty_scheduler(interval_seconds=60)

