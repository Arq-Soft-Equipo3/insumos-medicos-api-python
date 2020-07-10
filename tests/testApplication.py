from unittest import TestCase

from src.application import Application
from src.customExceptions import InstanceCreationFailed, StatusTransitionFailed


class TestApplication(TestCase):

    def test_instanceCreation(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos', None)

        self.assertEqual(application.filler, 'sarasa@hotmail.com')
        self.assertEqual(application.supply, 'Barbijos')
        self.assertEqual(application.area, 'Técnicos')
        self.assertEqual(application.status, 'Pending')

    def test_FieldsNotEmpty(self):
        with self.assertRaises(InstanceCreationFailed):
            Application('sarasa@hotmail.com', 'Barbijos', None, None)

    def test_cancelApplication(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos', None)
        application.cancel()

        self.assertEqual(application.status, 'Canceled')

    def test_approveApplication(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos', None)
        application.approveApplication()

        self.assertEqual(application.status, 'Accepted')

    def test_canceledApplicationCannotBeApproved(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos', None)
        application.cancel()

        with self.assertRaises(StatusTransitionFailed):
            application.approveApplication()
