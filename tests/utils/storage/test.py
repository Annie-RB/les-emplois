from django.test import override_settings

from tests.utils.test import TestCase


# The apply tests do use the S3 resource since part of the process consists in uploading a document.
@override_settings(
    S3_STORAGE_ENDPOINT_DOMAIN="localhost",
    S3_STORAGE_BUCKET_NAME="test",
    S3_STORAGE_ACCESS_KEY_ID="minioadmin",
    S3_STORAGE_SECRET_ACCESS_KEY="minioadmin",
)
class S3AccessingTestCase(TestCase):
    pass
    # @classmethod
    # def setUpClass(cls):
    #     super().setUpClass()
    #     namespace = uuid.uuid4()
    #     original_location = default_storage.location
    #     default_storage.location = f"{original_location}/{namespace}"

    #     def cleanup():
    #         default_storage.location = original_location

    #     cls.addClassCleanup(cleanup)
