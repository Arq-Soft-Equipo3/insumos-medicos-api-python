from unittest import TestCase

from src.application import Application


class TestApplication(TestCase):

    def test_instanceCreation(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos')

        self.assertEqual(application.filler, 'sarasa@hotmail.com')
        self.assertEqual(application.supply, 'Barbijos')
        self.assertEqual(application.area, 'Técnicos')
        self.assertEqual(application.status, 'Pending')

    def test_FieldsNotEmpty(self):
        with self.assertRaises(ValueError):
            Application('sarasa@hotmail.com', 'Barbijos', None)

    def test_cancelApplication(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos')
        application.cancelApplication()

        self.assertEqual(application.status, 'Canceled')

    def test_approveApplication(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos')
        application.approveApplication()

        self.assertEqual(application.status, 'Accepted')

    def test_canceledApplicationCannotBeApproved(self):
        application = Application('sarasa@hotmail.com', 'Barbijos', 'Técnicos')
        application.cancelApplication()

        with self.assertRaises(ValueError):
            application.approveApplication()
