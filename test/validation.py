from unittest import TestCase
from .mock import UniqueForm, PhoneForm
from server import app


class ValidationTest(TestCase):
    def test_unique_validation(self):
        params = {
            'items': ['1', '2']
        }

        app.config['TESTING'] = True

        with app.test_client():
            with app.app_context():
                form = UniqueForm(**params)

                self.assertTrue(form.validate())

    def test_duplicate_validation(self):
        params = {
            'items': ['2', '2']
        }

        app.config['TESTING'] = True

        with app.test_client():
            with app.app_context():
                form = UniqueForm(**params)

                # should give error
                self.assertFalse(form.validate())

    def test_valid_phone_number(self):
        params = {
            'phone': '+905399228080'
        }

        app.config['TESTING'] = True

        with app.test_client():
            with app.app_context():
                form = PhoneForm(**params)

                # should give error
                self.assertTrue(form.validate())

    def test_invalid_phone_number(self):
        params1 = {
            'phone': '0905399228080'
        }

        params2 = {
            'phone': '+9053992280'
        }

        app.config['TESTING'] = True

        with app.test_client():
            with app.app_context():
                form1 = PhoneForm(**params1)

                # should give error
                self.assertFalse(form1.validate())

                form2 = PhoneForm(**params2)

                # should give error
                self.assertFalse(form2.validate())
