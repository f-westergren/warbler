""" User views tests """

import os
from unittest import TestCase
from flask import session

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

class UserViewTestCase(TestCase):
	"""Test views for users """

	def setUp(self):
		db.drop_all()
		db.create_all()

		self.uid = 94566
		u = User.signup("testuser", "testing@test.com", "password", None)
		u.id = self.uid
		db.session.commit()

		self.u = User.query.get(self.uid)

		self.client = app.test_client()

	
	def test_list_users_view(self):
		""" Test list users view """
		resp = self.client.get('/users')
		html = resp.get_data(as_text=True)

		self.assertEqual(resp.status_code, 200)
		self.assertIn(f'<p>@{self.u.username}</p>', html)
	
	def test_show_user_view(self):
		""" Test user detail view """
		resp = self.client.get(f'/users/{self.u.id}')
		html = resp.get_data(as_text=True)

		self.assertEqual(resp.status_code, 200)
		self.assertIn(f'<h4 id="sidebar-username">@{self.u.username}</h4>', html)
	
	def test_show_following(self):
		print('sess', session)
		with self.client.session_transaction() as change_session:
			change_session['curr_user'] = self.uid

			resp = self.client.get(f'/users/{self.uid}/following')
		
			
			self.assertEqual(resp.status_code, 200)
		
	
		