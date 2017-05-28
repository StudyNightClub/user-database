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
            'home_city': '',
            'home_distinct': '',
            'home_road': '',
            'office_city': '',
            'offict_distinct': '',
            'offict_road': '',
            'undistrubed_start': '23:00',
            'undistrubed_end': '07:00',
            'subscribe_type': 'all',
            'feedback': '',
            'filter_on': True,
            'active_nofity': '17:00',
    }


class DBHandler(object):
    # FIXME Here we used a user_dict of list to standfor user_db
    # json dump & load is a temporary replacement for sqlite db command
    db = []
    db_path = ''
    db_opened = False

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
            print('==========')
            for key, val in row.items():
                print('{}: {}'.format(key, val))

db = DBHandler()


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
        self.db_path = db_path
        pass

    def list_all_user(self):
        '''
        Return a list of all users in db.
        '''
        pass

    def get_user(self, user_id):
        '''
        Get a user dict by givin a user id.
        If user id is not exist, return None, else return user_dict
        '''
        pass


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
            raise IOError('db_path=[{}] not exist'.format(db_path))

        self.db_path = db_path

    def create_db(self):
        '''
        Create an empty databasa.
        If db has already exist, raise IOError.
        '''
        if os.path.exists(self.db_path):
            raise IOError('db [{}] already exist'.format(self.db_path))


    def add_user(self):
        '''
        Add a new user into db by a user dict.
        '''
        pass

    def update_user(self, user_dict):
        '''
        Update a user data by user dict. Only update the exist keys.
        If key is not on the user_dict format, then raise KeyError.
        '''
        pass

    def remove_user(self, user_id):
        '''
        Remove user from db by a user id.
        If user is not exist, raise ValueError.
        '''
        pass


if '__main__' == __name__:
    print('main test')

    print('=============')

    print('test db open')
    db.open('test.db')
    db.print()
    print('test db close')
    db.close()

    db.open('test.db')

    row1 = {'a':1, 'b':2, 'c':3}
    row2 = {'a':11, 'b':22, 'c':33}

    print('test insert row')
    db.insert_row(row1)
    db.print()

    print('test insert row')
    db.insert_row(row2)
    db.print()

    print('test update key a to xx where b is 2')
    db.update('a', 'xx', 'b', 2)
    db.print()

    print('test quert key a where b is 22')
    print(db.query('a', 'b', 22))

    print('test dump')
    print(db.dump())

    db.close()





