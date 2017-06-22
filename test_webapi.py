#!/bin/python3
# -*- coding: utf-8 -*-

import os
import json
import requests
import urllib
from urllib.parse import urljoin, urlencode
from urllib.request import Request, urlopen
import unittest
import userdatabase

db_url = 'http://tingshengchu.myds.me:8888'
db_token = ''

def load_token():
    global db_token
    with open('secret.key', 'r') as f:
        db_token = f.read().strip()
    print('token loaded = [{}]'.format(db_token))

def send_webapi(method, path, args={}, data={}):
    send_url = urljoin(db_url, path) + '?' + 'userToken={}'.format(db_token)
    for key, val in args:
        send_url = send_url + '&' + key + '=' + val

    if not data:
        send_enc_data = None
    else:
        send_enc_data = urlencode(data).encode('utf-8')

    req = Request(url=send_url, method=method, data=send_enc_data)
    resp = urlopen(req)

    if resp.code != 200:
        print('req.method=[{}]'.format(req.method))
        print('rep.url=[{}]'.format(rep.url))
        print('resp.getcode=[{}]'.format(resp.getcode()))
        raise IOError('send webapi failed.')

    return resp.read().decode('utf-8')

def get_user_list():
    msg = send_webapi('GET', '/user/0')
    user_list = json.loads(msg)
    if type(user_list) is not list:
        raise TypeError('user_list is not a list')
    else:
        return user_list

class TestDBReaderWebapi(unittest.TestCase):
    def setUp(self):
        print('\n')

    def test_list_all_user(self):
        msg = send_webapi('GET', '/user/0')
        self.assertIsNotNone(msg)
        l = json.loads(msg)
        print('user list:', l)
        self.assertTrue(type(l) is list)

    def test_get_user(self):
        user_list = get_user_list()
        if not user_list:
            raise unittest.SkipTest('No users in db')

        default_db_keys = set(userdatabase.get_default_row().keys())
        for user in user_list:
            msg = send_webapi('GET', '/user/'+user)
            self.assertIsNotNone(msg)
            u = json.loads(msg)
            self.assertIsNotNone(u)
            print('get user:[{}]'.format(user))
            user_keys = set(u.keys())
            self.assertEqual(user_keys, default_db_keys)

    def test_get_setting_page(self):
        user_list = get_user_list()
        self.assertIsNotNone(user_list)

        if not user_list:
            raise unittest.SkipTest('No users in db')

        for user in user_list:
            msg = send_webapi('GET', '/setting/'+user)
            self.assertIsNotNone(msg)

class TestDBWriterWebapi(unittest.TestCase):
    def setUp(self):
        print('\n')

    def test_create_user(self):
        curr_user_list = get_user_list()
        if not curr_user_list:
            raise unittest.SkipTest('No users in db')
        print('curr user list:', curr_user_list)

        user = userdatabase.get_default_row()

        user_id = ''
        for i in range(1, 100):
            user_id = 'unittest_' + str(i)
            if user_id not in curr_user_list:
                user['id'] = user_id
                break
        else:
            raise unittest.SkipTest('Cannot find candidate of user id')

        data = {'data': json.dumps(user)}

        msg = send_webapi('PUT', '/user/'+user_id, data=data)
        print('create msg:', msg)
        self.assertIsNotNone(msg)
        self.assertTrue('created' in msg)

        new_user_list = get_user_list()
        print('new user list:', new_user_list)
        self.assertTrue(user_id in new_user_list)

    def test_delete_user(self):
        curr_user_list = get_user_list()
        if not curr_user_list:
            raise unittest.SkipTest('No users in db')
        print('curr user list:', curr_user_list)

        user_id = ''
        for user in curr_user_list:
            if user.startswith('unittest_'):
                user_id = user
                break
        else:
            raise unittest.SkipTest('Cannot find unittest user for delete')

        msg = send_webapi('DELETE', '/user/'+user_id)
        self.assertIsNotNone(msg)
        print('delete msg:', msg)
        self.assertTrue('deleted' in msg)

        new_user_list = get_user_list()
        print('new user list:', new_user_list)
        self.assertTrue(user_id not in new_user_list)

    def test_update_user(self):
        pass

    def test_post_setting_page(self):
        pass

@unittest.skip("skip tests of other webapi")
class TestDBSenarioWebapi(unittest.TestCase):
    pass

class TestWebapi(unittest.TestCase):
    def setUp(self):
        print('\n')

    def test_address_to_geocord(self):
        address = '台北市中山區民生東路一段'
        url_address = 'http://maps.googleapis.com/maps/api/geocode/json?address=' + urllib.parse.quote(address) + '&sensor=false&language=zh-tw'

        req = Request(url_address)
        resp = urlopen(req)

        if resp.code == 200:
            location = json.loads(resp.read().decode('utf-8'))
            print(location['results'][0]['geometry']['location'])
            self.assertIsNotNone(location['results'][0]['geometry']['location']['lat'])
            self.assertIs(type(location['results'][0]['geometry']['location']['lat']), float)
            self.assertIsNotNone(location['results'][0]['geometry']['location']['lng'])
            self.assertIsNotNone(type(location['results'][0]['geometry']['location']['lng']), float)
        else:
            self.fail('code=[{}]'.format(resp.code))

    def test_api_post_after_user_update(self):
        data={'userId': 'test_user_id'}
        post_data = json.dumps(data).encode('utf-8')

        req = Request(
                headers={"Content-Type": "application/json" },
                url='https://glacial-falls-53180.herokuapp.com/setting/webhook',
                method='POST',
                data=post_data
                )
        resp = urlopen(req)
        self.assertEqual(200, resp.getcode())
        self.assertEqual(b'{}', resp.read())

if '__main__' == __name__:
    load_token()
    unittest.main(verbosity=2)

