""" Message model tests """

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, Message, User, Likes

# Does the repr method work as expected?
# Does basic model work?
# Does model fail when not including text?
# Does user relationship work?

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

class MessageModelTestCase(TestCase):
	"""Test Message Model """
	def setUp(self):
		db.drop_all()
		db.create_all()

		u1 = User.signup("user1", "user1@test.com", "password", None)
		u1id = 9999
		u1.id = u1id
		db.session.add(u1)
		db.session.commit()

		self.u1 = User.query.get(9999)
	
	def tearDown(self):
		db.session.rollback()
	

	def test_message_model(self):
		""" Does basic model work? """

		m = Message(
			text="My test post.",
			user_id=self.u1.id
		)

		m.id = 8888

		db.session.add(m)
		db.session.commit()

		msg = Message.query.get(8888)

		self.assertEqual(msg.text, "My test post.")
		self.assertEqual(msg.user_id, 9999)
	
	def test_no_user_id(self):

		m = Message(
			text="My test post with no user."
		)

		db.session.add(m)

		with self.assertRaises(exc.IntegrityError) as context:
			db.session.commit()
	
	def test_no_text(self):
		m = Message(
			user_id=9999
		)
		
		db.session.add(m)

		with self.assertRaises(exc.IntegrityError) as context:
			db.session.commit()
	
	def test_user_relationship(self):
		
		m = Message(
			text="I am a test post"
		)

		self.u1.messages.append(m)

		db.session.commit()

		self.assertEqual(self.u1.messages[0], m)
	
	def test_message_likes(self):
		m = Message(
			text="I am a test message"
		)

		self.u1.messages.append(m)
		u2 = User.signup("user2", "user2@test.com", "password", None)
		u2.likes.append(m)
		db.session.add_all([u2, m])
		db.session.commit()

		self.assertEqual(u2.likes[0], m)

		
