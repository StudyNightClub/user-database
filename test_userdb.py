#!/usr/local/bin/Python3

import os
import unittest
import userdatabase

class TestUserDB(unittest.TestCase):
    db_path = 'unittest.db'

    def setUp(self):
        print('test setup')
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_create_userdb(self):
        self.assertFalse(os.path.exists(self.db_path))
        with userdatabase.UserDBWriter(self.db_path) as writer:
            pass
        self.assertTrue(os.path.exists(self.db_path))

    def test_adduser(self):
        user_id = 'user_id_1'
        row = userdatabase.get_default_row()
        row['id'] = user_id

        with userdatabase.UserDBWriter(self.db_path) as writer:
            writer.add_user(row)

        with userdatabase.UserDBReader(self.db_path) as reader:
            users = reader.list_all_user()
            self.assertTrue(user_id in users)
            row = reader.get_user(user_id)
            self.assertTrue(row)

    def test_writer_updateuser(self):
        user_id = 'user_id_1'
        row = userdatabase.get_default_row()
        row['id'] = user_id

        with userdatabase.UserDBWriter(self.db_path) as writer:
            writer.add_user(row)

        with userdatabase.UserDBReader(self.db_path) as reader:
            user = reader.get_user(user_id)
            self.assertFalse(user['name'])

        row['name'] = 'username1'
        with userdatabase.UserDBWriter(self.db_path) as writer:
            writer.update_user(row)

        with userdatabase.UserDBReader(self.db_path) as reader:
            user = reader.get_user(user_id)
            self.assertTrue(user['name']=='username1')

    def test_removeuser(self):
        user_id = 'user_id_1'
        row = userdatabase.get_default_row()
        row['id'] = user_id

        with userdatabase.UserDBWriter(self.db_path) as writer:
            writer.add_user(row)

        with userdatabase.UserDBReader(self.db_path) as reader:
            users = reader.list_all_user()
            self.assertTrue(user_id in users)
            row = reader.get_user(user_id)
            self.assertTrue(row)

        with userdatabase.UserDBWriter(self.db_path) as writer:
            writer.remove_user(user_id)

        with userdatabase.UserDBReader(self.db_path) as reader:
            users = reader.list_all_user()
            self.assertFalse(users)


if '__main__' == __name__:
    unittest.main(verbosity=2)

