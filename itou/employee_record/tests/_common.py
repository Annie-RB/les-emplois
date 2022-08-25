from io import StringIO

from django.core import management
from django.test import TestCase


class ManagementCommandTestCase(TestCase):

    # Override as needed
    MANAGEMENT_COMMAND_NAME = None

    def call_command(self, management_command_name=None, *args, **kwargs):
        """Redirect standard outputs from management command to StringIO objects for testing purposes."""

        out = StringIO()
        err = StringIO()
        command = self.MANAGEMENT_COMMAND_NAME or management_command_name

        assert command, "Management command name must be provided"

        management.call_command(
            command,
            *args,
            stdout=out,
            stderr=err,
            **kwargs,
        )

        return out.getvalue(), err.getvalue()
