#!/bin/python3

from flask import Flask, session, redirect, url_for, escape, request, render_template
from flask import safe_join, make_response
import userdatabase
import logging
import urllib
import json
import os

app = Flask(__name__)
log = logging.getLogger('werkzeug')

db_path = 'userdata.db'

@app.route('/')
def index():
    if not token_check(request):
        return 'Permission Insufficient'

    log.debug('request form=[{}]'.format(request.form))
    return 'Index Page'

@app.route('/templates/<path:path>', methods=['GET'])
def send_template(path):
    template_path = safe_join('templates', path)
    if not os.path.exists(template_path):
        return 'path not exist = [{}]'.format(template_path)

    content = ''
    with open(template_path, 'r+b') as f:
        content = f.read()

    resp = make_response(content)
    if path.endswith('css'):
        resp.headers['Content-Type'] = 'text/css'
    else:
        resp.headers['Content-Type'] = 'text/html'

    return resp

@app.route('/setting/<user_id>', methods=['GET', 'POST'])
def setting(user_id):
    if not token_check(request):
        return 'Permission Insufficient'

    log.debug('request form=[{}]'.format(request.form))

    bool_key = ['filter_on', 'subscribe_water', 'subscribe_electricity', 'subscribe_road']

    if request.method == 'GET':
        user = {}
        with userdatabase.UserDBReader(db_path) as reader:
            user = reader.get_user(user_id)
        if user is None:
            return 'User [{}] is not found'.format(user_id)

        # make boolean show checked in html checkbox
        for key in bool_key:
            if user[key] is True:
                user[key] = 'checked'
            else:
                user[key] = ''

        return render_template('setting_web.html',
                user=user,
                user_token=request.args.get('userToken', ''),
                show_success=request.args.get('show_success', 'none'))

    elif request.method == 'POST':
        form_keys = list(request.form.keys())
        update_data = {}
        for k in form_keys:
            update_data[k] = request.form[k]

        #make checked become boolean in database
        for key in bool_key:
            if key in form_keys and request.form[key] == 'on':
                update_data[key] = True
            else:
                update_data[key] = False

        row = {}
        with userdatabase.UserDBReader(db_path) as reader:
            row = reader.get_user(user_id)

        row.update(update_data)

        # get geo cord by address
        geocord = address_to_geocord(
                update_data['interest_city']+update_data['interest_district']+update_data['interest_road'])

        if geocord:
            row.update(geocord)

        with userdatabase.UserDBWriter(db_path) as writer:
            writer.update_user(row)

        return redirect(request.url + '&show_success=block')

    else:
        return 'not support method=[%s]'.format(request.method)

@app.route('/user/<user_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user(user_id):
    if not token_check(request):
        return 'Permission Insufficient'

    log.debug('request form=[{}]'.format(request.form))

    # FIXME check user_id is valid format, if not then return error message


    if request.method == 'GET':
        with userdatabase.UserDBReader(db_path) as reader:
            if '0' == user_id:
                users = reader.list_all_user()
                return json.dumps(users)
            else:
                row = reader.get_user(user_id)
                return json.dumps(row)

    elif request.method == 'POST':
        row  = {}
        print('This is POST data=[%s]' % request.form['data'])
        with userdatabase.UserDBReader(db_path) as reader:
            row = reader.get_user(user_id)

        update_data = json.loads(request.form['data'])
        row.update(update_data)

        with userdatabase.UserDBWriter(db_path) as writer:
            writer.update_user(row)

        return 'user_id=[%s] updated=[%s]' % (user_id, json.dumps(row))

    elif request.method == 'PUT':
        if not request.form.get('data', ''):
            return 'get form data fail'

        log.debug('This is PUT data=[%s]' % request.form['data'])

        try:
            user_data = json.loads(request.form['data'])
        except Exception as e:
            return 'fail to json loads = [{}]\n'.format(request.form['data']) + e.msg

        default_row = userdatabase.get_default_row()

        if user_id != user_data['id']:
            return "user_id=[{}] did not match user_data['id']=[{}]".format(user_id, user_data['id'])

        user_data_keys = set(user_data.keys())
        default_row_keys = set(default_row.keys())

        if 'id' not in user_data_keys:
            return 'input user data is lack of value of id'

        for key in user_data_keys:
            default_row[key] = user_data[key]

        with userdatabase.UserDBReader(db_path) as reader:
            users = reader.list_all_user()
            if user_data['id'] in users:
                return "user [{}] is already exists".format(user_data['id'])

        with userdatabase.UserDBWriter(db_path) as writer:
            writer.add_user(default_row)

        return 'user [{}] is created'.format(user_id)

    elif request.method == 'DELETE':
        with userdatabase.UserDBReader(db_path) as reader:
            users = reader.list_all_user()
            if user_id not in users:
                return "user [{}] is not exist".format(user_id)

        with userdatabase.UserDBWriter(db_path) as writer:
            writer.remove_user(user_id)

        return "user [{}] is deleted".format(user_id)

    else:
        return 'not support method=[%s]'.format(request.method)

def address_to_geocord(address):
    #address = '台北市中山區民生東路一段'
    geocord = {
            'longitude': 0.0,
            'latitude': 0.0
            }

    if not address:
        return geocord

    url_address = 'http://maps.googleapis.com/maps/api/geocode/json?address=' + urllib.parse.quote(address) + '&sensor=false&language=zh-tw'

    req = urllib.request.Request(url_address)
    resp = urllib.request.urlopen(req)

    if resp.code != 200:
        return None

    location = json.loads(resp.read().decode('utf-8'))

    if location['status'] == 'ZERO_RESULTS':
        return None

    print(location['results'][0]['geometry']['location'])
    geocord['longitude'] = location['results'][0]['geometry']['location']['lng']
    geocord['latitude'] = location['results'][0]['geometry']['location']['lat']
    return geocord

def daemonize(setsid = True):
    import os, time, sys
    pid = os.fork()
    if 0 != pid:
        time.sleep(1)
        exit(0)

    if setsid:
        os.setsid()

    pid = os.fork()
    if 0 != pid: exit(0)

def set_logger():
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s")
    handler = logging.FileHandler('daemon.log')
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)

def token_load():
    with open('secret.key', 'r') as f:
        return f.read().strip()

def token_check(request):
    user_token = request.args.get('userToken','')
    if user_token == auth_token:
        return True
    else:
        return False

if __name__ == '__main__':
    auth_token = token_load()
    set_logger()
    #daemonize()
    app.run(host='0.0.0.0', port=8888, debug=True, threaded=True)


