#!/usr/local/bin/Python3

import os
import json
import sqlite3

def get_default_row():
    '''
    return a dict with default keys and values to represent a user data row
    '''
    return {
            'id': '',
            'name': '',
            'interest_city': '',
            'interest_district': '',
            'interest_road': '',
            'office_city': '',
            'office_district': '',
            'office_road': '',
            'undisturbed_start': '23:00',
            'undisturbed_end': '07:00',
            'subscribe_water': True,
            'subscribe_electricity': True,
            'subscribe_road': True,
            'feedback': '',
            'filter_on': False,
            'active_notify': '17:00',

            # hidden column
            'longitude': 0.0,
            'latitude': 0.0,
    }


class DBHandler(object):
    # FIXME Here we used a user_dict of list to standfor user_db
    # json dump & load is a temporary replacement for sqlite db command

    def __init__(self):
        self.db = []
        self.db_path = ''
        self.db_opened = False

    def open(self, db_path):
        self.db_path = db_path

        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump(self.db, f)
        else:
            with open(self.db_path, 'r') as f:
                self.db = json.load(f)

        self.db_opened = True

    def close(self):
        if not self.db_opened:
            raise IOError('please open db first.')

        with open(self.db_path, 'w') as f:
            json.dump(self.db, f)

        self.db_opened = False

    def insert_row(self, row):
        if not self.db_opened:
            raise IOError('please open db first.')

        if type(row) is not dict:
            raise TypeError('inpur row is not a type of dict')
        self.db.append(row)

    def delete_row(self, key, val):
        if not self.db_opened:
            raise IOError('please open db first.')

        for row in self.db:
            if val == row[key]:
                self.db.remove(row)

    def update(self, update_key, update_value, where_key, where_value):
        if not self.db_opened:
            raise IOError('please open db first.')

        for row in self.db:
            if where_value == row[where_key]:
                row[update_key] = update_value
                return True
        else:
            return False

    def query(self, query_key, where_key, where_value):
        if not self.db_opened:
            raise IOError('please open db first.')

        for row in self.db:
            if where_value == row[where_key]:
                return row[query_key]
        else:
            return None

    def dump(self):
        if not self.db_opened:
            raise IOError('please open db first.')

        return self.db

    def print(self):
        if not self.db_opened:
            raise IOError('please open db first.')

        for row in self.db:
            print('---')
            for key, val in row.items():
                print('{}: {}'.format(key, val))


class UserDBReader(object):
    '''
    Use this class for all user db read action.
    e.g. Web service daemon, main function, notification engine, line bot
    '''
    def __init__(self, db_path):
        '''
        Initialize object with a db_path.
        If db is not exist, raise IOError.
        '''
        if not os.path.exists(db_path):
            raise IOError('db_path [{}] is not esxit'.format(db_path))

        self.db_path = db_path
        self.db = DBHandler()

    def __enter__(self):
        self.db.open(self.db_path)
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def list_all_user(self):
        '''
        Return a list of all users in db.
        '''
        users = []
        for row in self.db.dump():
            users.append(row['id'])
        return users

    def get_user(self, user_id):
        '''
        Get a user dict by givin a user id.
        If user id is not exist, return None, else return user_dict
        '''
        for row in self.db.dump():
            if user_id == row['id']:
                return row

class UserDBWriter(object):
    '''
    Use this class for all user db write action.
    e.g. Web service daemon
    '''

    def __init__(self, db_path):
        '''
        Initialize object with a db_path
        If db_path is None, raise ValueError.
        '''
        if not db_path:
            raise IOError('db_path [{}] is empty')

        self.db_path = db_path
        self.db = DBHandler()

    def __enter__(self):
        self.db.open(self.db_path)
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()

    def add_user(self, user_dict):
        '''
        Add a new user into db by a user dict.
        '''
        def_keys = list(get_default_row().keys())
        user_keys = user_dict.keys()

        for key in user_keys:
            if key in def_keys:
                def_keys.remove(key)
            else:
                raise KeyError('key [{}] is not belong user_dict'.format(key))

        if def_keys:
            raise KeyError('keys [{}] are not assigned'.format(def_keys))

        self.db.insert_row(user_dict)

    def update_user(self, user_dict):
        '''
        Update a user data by user dict. Only update the exist keys.
        If key is not on the user_dict format, then raise KeyError.
        '''
        def_keys = list(get_default_row().keys())
        user_keys = user_dict.keys()

        for key in user_keys:
            if key in def_keys:
                def_keys.remove(key)
            else:
                raise KeyError('key [{}] is not belong user_dict'.format(key))

        user_id = user_dict['id']
        for key, val in user_dict.items():
            if 'id' == key:
                continue
            self.db.update(key, val, 'id', user_id)

    def remove_user(self, user_id):
        '''
        Remove user from db by a user id.
        If user is not exist, raise ValueError.
        '''
        self.db.delete_row('id', user_id)


if '__main__' == __name__:
    print('main test')

    print('=============')

    db = DBHandler()

    print('test db open')
    db.open('test.db')
    db.print()
    print('test db close')
    db.close()

    db.open('test.db')

    row1 = {'id':'aa', 'b':2, 'c':3}
    row2 = {'id':'bb', 'b':22, 'c':33}

    print('test insert row')
    db.insert_row(row1)
    db.print()

    print('test insert row')
    db.insert_row(row2)
    db.print()

    print('test update key b to 222222 where id is aa')
    db.update('b', '2222222', 'id', 'aa')
    db.print()

    print('test quert key a where b is 22')
    print(db.query('b', 'id', 'aa'))

    print('test dump')
    print(db.dump())

    print('test remove')
    db.delete_row('id', 'aa')
    print(db.dump())

    db.close()

    print('=============')





