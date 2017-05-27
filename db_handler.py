#!/usr/local/bin/Python3

import os
import json
import sqlite3

# FIXME Here we used a user_dict of list to standfor user_db
# json dump & load is a temporary replacement for sqlite db command
user_db = []

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
        self.db_path = db_path
        pass

    def create_db(self):
        '''
        Create an empty databasa.
        If db has already exist, raise IOError.
        '''
        pass

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
    row = get_default_row()
    for key, val in row.items():
        print('{}: {}'.format(key, val))

    row['subscribe_type'] = 'elec'
    print(row['subscribe_type'])


















