#!/usr/local/bin/Python3

from flask import Flask, session, redirect, url_for, escape, request, render_template
import userdatabase
import json

app = Flask(__name__)

db_path = 'userdata.db'

@app.route('/')
def index():
    return 'Index Page'

@app.route('/setting/<user_id>', methods=['GET', 'POST', 'PUT'])
def setting(user_id):
    if request.method == 'GET':
        user = {}
        with userdatabase.UserDBReader(db_path) as reader:
            user = reader.get_user(user_id)
        return render_template('setting_web.html', user=user)
    elif request.method == 'POST':
        print('request:')
        print(request.form)
        return 'POSTED'
    else:
        return 'not support method=[%s]'.format(request.method)

@app.route('/user/<user_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user(user_id):
    # check user_id is valid format, if not then return error message

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
        user_data = json.loads(request.form['data'])
        default_row = userdatabase.get_default_row()

        if user_id != user_data['id']:
            return "user_id=[{}] did not match user_data['id']=[{}]".format(user_id, user_data['id'])

        if not set(user_data.keys()) == set(default_row.keys()):
            return "user_data keys is not match {}".format(user_data.keys())

        with userdatabase.UserDBReader(db_path) as reader:
            users = reader.list_all_user()
            if user_data['id'] in users:
                return "user [{}] is already exists".format(user_data['id'])

        with userdatabase.UserDBWriter(db_path) as writer:
            writer.add_user(user_data)

        return 'user [%s] is created' % (user_id, json.dumps(user_data))

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)



