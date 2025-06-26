from storages.backends.s3 import S3Storage
from django.conf import settings


class StaticFileStorage(S3Storage):
    """Static file storage for Cloudflare R2"""

    location = "static"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure we're using the correct configuration
        if hasattr(settings, "CLOUDFLARE_R2_CONFIG_OPTIONS"):
            for key, value in settings.CLOUDFLARE_R2_CONFIG_OPTIONS.items():
                if hasattr(self, key):
                    setattr(self, key, value)


class MediaFileStorage(S3Storage):
    """Media file storage for Cloudflare R2"""

    location = "media"
    file_overwrite = False  # This prevents overwrites

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure we're using the correct configuration
        if hasattr(settings, "CLOUDFLARE_R2_CONFIG_OPTIONS"):
            for key, value in settings.CLOUDFLARE_R2_CONFIG_OPTIONS.items():
                if hasattr(self, key):
                    setattr(self, key, value)
