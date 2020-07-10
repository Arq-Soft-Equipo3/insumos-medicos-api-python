from unittest import TestCase

import bcrypt

from src.customExceptions import InstanceCreationFailed
from src.user import User


class TestUser(TestCase):

    def setUp(self):
        self.validEmail = 'bokitaElMasGrande@oulsinectis.com.ar'
        self.invalidEmail= 'sasasa.com'

    def test_instanceCreation(self):
        newUser = User(self.validEmail, '132456', '132456', '1168727790', 'PAMI', 'Gerente de insumos', 'Domselaar')

        self.assertEqual(newUser.email, self.validEmail)
        self.assertEqual(newUser.phoneNumber, 1168727790)
        self.assertEqual(newUser.organization, 'PAMI')
        self.assertEqual(newUser.position, 'Gerente de insumos')
        self.assertEqual(newUser.city, 'Domselaar')

    def test_invalidEmailRaiseException(self):
        with self.assertRaises(InstanceCreationFailed):
            User(self.invalidEmail, '132456', '132456','1168727790', 'PAMI', 'Gerente de insumos', 'Domselaar')

    def test_instanceCreationFailed(self):
        with self.assertRaises(InstanceCreationFailed):
            User(self.validEmail, '132456', '132456','1168727790', 'PAMI', 'Gerente de insumos', None)

    def test_passwordsDoNotMatch(self):
        with self.assertRaises(InstanceCreationFailed):
            User(self.validEmail, '132456', 'sarasa', '1168727790', 'PAMI', 'Gerente de insumos', 'Domselaar')
