"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_add_no_session(self):
        """ Test add message when not logged in """

        res = self.client.post('/messages/new', data={"text": "Hello"})

        # Make sure it redirects
        self.assertEqual(res.status_code, 302)
        
        msg = Message.query.first()

        self.assertIsNone(msg)


    def test_add_invalid_user(self):
        """ Test add message when invalid user """
        with self.client.session_transaction() as session:
            session[CURR_USER_KEY] = 12234456 # user does not exist

        res = self.client.post('/messages/new', data={"text": "Hello"})
        self.assertEqual(res.status_code, 302)

        msg = Message.query.first()

        self.assertIsNone(msg)

    def test_message_show(self):
        """ Test if message shows up"""
        m = Message(text="A test message", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        res = self.client.get(f'/messages/{m.id}')

        self.assertEqual(res.status_code, 200)
        self.assertIn('A test message', str(res.data))


    def test_invalid_message_show(self):
        """ Test if invalid message doesn't show up"""
        res = self.client.get('/messages/1234') # message does not exist

        self.assertEqual(res.status_code, 404)
    
    def create_test_message(self):
        m = Message(text="A test message", user_id=self.testuser.id)
        m.id = 12345
        db.session.add(m)
        db.session.commit()

        # Check that message exists:
        msg = Message.query.get(m.id)
        self.assertEqual(msg.text, 'A test message')

    def test_message_delete(self):
        """ Test that user can delete own messages """
        self.create_test_message()

        with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id
        res = self.client.post(f'/messages/12345/delete')

        self.assertEqual(res.status_code, 302)
    
        # Check that message has been deleted
        self.assertIsNone(Message.query.get(12345))

    def test_unathorized_message_delete(self):
        """ Test that user can't delete other messages """

        self.create_test_message()

        with self.client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser2.id
        res = self.client.post(f'/messages/12345/delete')      

        self.assertEqual(res.status_code, 302) 
        
        # Check that message still exists.
        msg = Message.query.get(12345)
        self.assertEqual(msg.text, 'A test message')

    def test_message_delete_no_authentication(self):
        """ Test if not logged in user can delete message """

        self.create_test_message()

        res = self.client.post(f'/messages/12345/delete')

        self.assertEqual(res.status_code, 302) 

        # Check that message still exists.
        msg = Message.query.get(12345)
        self.assertEqual(msg.text, 'A test message')
