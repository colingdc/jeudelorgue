import unittest

from app import create_app, db
from app.models import User, AnonymousUser
from app.roles import Role


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password="cat")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password="cat")
        with self.assertRaises(AttributeError):
            print(u.password)

    def test_password_verification(self):
        u = User(password="cat")
        self.assertTrue(u.verify_password("cat"))
        self.assertFalse(u.verify_password("dog"))

    def test_password_salts_are_random(self):
        u = User(password="cat")
        u2 = User(password="cat")
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password="cat")
        u2 = User(password="dog")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_valid_reset_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, "dog"))
        self.assertTrue(u.verify_password("dog"))

    def test_invalid_reset_token(self):
        u1 = User(password="cat")
        u2 = User(password="dog")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, "horse"))
        self.assertTrue(u2.verify_password("dog"))

    def test_role_user(self):
        u = User(role_id=Role.USER.id)
        self.assertFalse(u.is_manager())
        self.assertFalse(u.is_administrator())

    def test_role_manager(self):
        u = User(role_id=Role.MANAGER.id)
        self.assertTrue(u.is_manager())
        self.assertFalse(u.is_administrator())

    def test_role_administrator(self):
        u = User(role_id=Role.ADMINISTRATOR.id)
        self.assertTrue(u.is_manager())
        self.assertTrue(u.is_administrator())

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.is_manager())
        self.assertFalse(u.is_administrator())
