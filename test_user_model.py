"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data




class UserModelTestCase(TestCase):
    """ Test User Model """

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("user1", "user1@test.com", "password", None)
        u1id = 9999
        u1.id = u1id
        db.session.add(u1)

        u2 = User.signup("user2", "user2@test.com", "password", None)
        u2id = 9998
        u2.id = u2id
        db.session.add(u2)

        db.session.commit()

        self.client = app.test_client()
        self.u1 = User.query.get(u1id)
        self.u2 = User.query.get(u2id)
    
    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_following(self):
        """ Does following work? """

        # u1 should not be following u2
        self.assertEqual(len(self.u1.following), 0)

        f = Follows(user_being_followed_id=self.u2.id, user_following_id=self.u1.id)
        db.session.add(f)
        db.session.commit()

        # u1 should be following u2
        self.assertEqual(self.u1.following[0], self.u2)

    def test_is_followed_by(self):
        """ Does followers work? """

        # u1 should not be followed by u2
        self.assertEqual(len(self.u1.followers), 0)

        f = Follows(user_being_followed_id=self.u1.id, user_following_id=self.u2.id)
        db.session.add(f)
        db.session.commit()     

        # u1 should be followed by u2
        self.assertEqual(self.u1.followers[0], self.u2)
    
    def test_signup_user(self):
        """ Does signup user work? """
        
        u = User.signup("test", "user@test.com", "HASHED_PASSWORD", None)
        
        # u should be an instance of User class
        self.assertEqual(u.username, 'test')
        self.assertEqual(u.email, 'user@test.com')
        self.assertNotEqual(u.password, 'password')
        self.assertTrue(u.password.startswith('$2b$'))
    
    def invalid_signup_user(self):
        u_fail = User.signup('test_username')
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    

    def test_authenticate(self):
        u = User.authenticate(self.u1.username, "password")
        
        #u should be u1
        self.assertEqual(u, self.u1)

    def test_invalid_password(self):
        u = User.authenticate(self.u1.username, "wrongpassword")

        #u should be False
        self.assertFalse(u)
    
    def test_invalid_email(self):
        u = User.authenticate("nonexistentemail@test.com", "password")

        #u should be False
        self.assertFalse(u)