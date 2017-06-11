#!/usr/local/bin/Python3

from flask import Flask, session, redirect, url_for, escape, request, render_template, send_from_directory
import userdatabase
import logging
import json

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
    print('request tempate path=[{}]'.format(path))
    return send_from_directory('/templates', path)
    pass

@app.route('/setting/<user_id>', methods=['GET', 'POST'])
def setting(user_id):
    if not token_check(request):
        return 'Permission Insufficient'

    log.debug('request form=[{}]'.format(request.form))

    if request.method == 'GET':
        user = {}
        with userdatabase.UserDBReader(db_path) as reader:
            user = reader.get_user(user_id)
        if user is None:
            return 'User [{}] is not found'.format(user_id)
        else:
            return render_template('setting_web.html', user=user, user_token=request.args.get('userToken',''))
    elif request.method == 'POST':
        update_data = {}
        for k in request.form.keys():
            update_data[k] = request.form[k]

        row = {}
        with userdatabase.UserDBReader(db_path) as reader:
            row = reader.get_user(user_id)

        row.update(update_data)

        with userdatabase.UserDBWriter(db_path) as writer:
            writer.update_user(row)

        return 'user_id=[%s] updated=[%s]' % (user_id, update_data)
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


def daemonize(setsid = True):
    import os, time
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
    daemonize()
    app.run(host='0.0.0.0', port=8888, debug=True)


