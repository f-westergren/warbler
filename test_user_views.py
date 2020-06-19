""" User views tests """

import os
from unittest import TestCase
from flask import session

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app, CURR_USER_KEY

class UserViewTestCase(TestCase):
	"""Test views for users """

	def setUp(self):
		db.drop_all()
		db.create_all()

		u1 = User.signup("testuser", "testing@test.com", "password", None)
		u2 = User.signup("testuser2", "testing2@test.com", "password", None)
		u1.id = 11111
		u2.id = 22222
		u1.following.append(u2)

		m = Message(text='Test post', user_id=u2.id)
		m.id=12345

		u2.messages.append(m)
		db.session.commit()

		self.u1 = User.query.get(u1.id)
		self.u2 = User.query.get(u2.id)
		self.m = Message.query.get(m.id)
		self.client = app.test_client()
	
	def tearDown(self):
		db.session.rollback()
	
	def test_list_users_view(self):
		""" Test list users view """
		resp = self.client.get('/users')
		html = resp.get_data(as_text=True)

		self.assertEqual(resp.status_code, 200)
		self.assertIn(f'<p>@{self.u1.username}</p>', html)
	
	def test_show_user_view(self):
		""" Test user detail view """
		resp = self.client.get(f'/users/{self.u1.id}')
		html = resp.get_data(as_text=True)

		self.assertEqual(resp.status_code, 200)
		self.assertIn(f'<h4 id="sidebar-username">@{self.u1.username}</h4>', html)
	
	def test_show_following(self):
		"""Test user following"""

		# Log in user
		with self.client.session_transaction() as change_session:
			change_session['curr_user'] = self.u1.id

		resp = self.client.get(f'/users/{self.u1.id}/following')
		html = resp.get_data(as_text=True)

		# Make sure user can see its own followers				
		self.assertEqual(resp.status_code, 200)
		self.assertIn(f'<p>@{self.u2.username}</p>', html)

		# Make sure logged in users can see other followers
		resp = self.client.get(f'/users/{self.u2.id}/following')
		self.assertEqual(resp.status_code, 200)
	
	def test_show_following_not_logged_in(self):
		"""Test user following not logged in"""

		resp = self.client.get(f'/users/{self.u1.id}/following')
		
		# User should be redirected
		self.assertEqual(resp.status_code, 302)
	
	def test_show_followers(self):
		"""Test user followers view"""

		# Log in user
		with self.client.session_transaction() as change_session:
			change_session[CURR_USER_KEY] = self.u2.id

		resp = self.client.get(f'/users/{self.u2.id}/followers')
		html = resp.get_data(as_text=True)

		# Make sure user can see its own followers				
		self.assertEqual(resp.status_code, 200)
		self.assertIn(f'<p>@{self.u1.username}</p>', html)

		# Make sure logged in users can see other followers
		resp = self.client.get(f'/users/{self.u1.id}/following')
		self.assertEqual(resp.status_code, 200)
		
	def test_show_following_not_logged_in(self):
		"""Test user followers not logged in"""

		resp = self.client.get(f'/users/{self.u1.id}/followers')
		
		# User should be redirected
		self.assertEqual(resp.status_code, 302)
	
	def test_show_likes_not_logged_in(self):
		""" Test show likes not logged in"""

		resp = self.client.get(f'/users/{self.u1.id}/likes')

		# User should be redirected
		self.assertEqual(resp.status_code, 302)


	def test_add_and_delete_like(self):
		# Log in user
		with self.client.session_transaction() as session:
			session[CURR_USER_KEY] = self.u1.id

		# Add like
		res = self.client.post(f'/users/add_like/{self.m.id}',
			follow_redirects=True)
		html = res.get_data(as_text=True)

		# Check that like has been added to view
		self.assertEqual(res.status_code, 200)
		self.assertIn('action="/users/remove_like/', html)

		# Remove like
		res = self.client.post(f'/users/remove_like/{self.m.id}',
			follow_redirects=True)
		html = res.get_data(as_text=True)

		# Check that like has been removed from view
		self.assertEqual(res.status_code, 200)
		self.assertIn('action="/users/add_like/', html)