from typing import List
import unittest
import os
from app import app, db
from app.exceptions import InvalidFriendException, UserNotFoundException
from app.models import User, Friendship


class StudentModelCase(unittest.TestCase):

    def setUp(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] =\
            'sqlite:///'+os.path.join(basedir, 'test.db')


        self.app_context = app.app_context()
        self.app_context.push()
        self.app = app.test_client()  # creates a virtual test environment
        db.create_all()

        u1 = User(user_id='user1', display_name='User 1')
        u2 = User(user_id='user2', display_name='User 1')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_friend(self):
        user: User = User.query.filter(User.user_id == 'user1').first()
        user.add_friend('user2')

        self.assertRaises(InvalidFriendException, user.add_friend, 'user1')
        self.assertRaises(InvalidFriendException, user.add_friend, 'user2')
        self.assertRaises(UserNotFoundException, user.add_friend, 'user3')

        friends = user.friends
        self.assertTrue(friends[0].user_id == 'user2')

if __name__ == '__main__':
    unittest.main(verbosity=2)
