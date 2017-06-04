#!/usr/local/bin/Python3

from flask import Flask, url_for, render_template
from flask import render_template, request
app = Flask(__name__)

'''
@app.route('/')
def index():
    return 'Index Page'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route('/projects/')
def projects():
    return 'The project page'

with app.test_request_context():
    print url_for('index')
    print url_for('login')
    print url_for('login', next='/')
    print url_for('profile', username='John Doe')


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
'''


from flask import Flask, session, redirect, url_for, escape, request
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
        with open('setting_web.html', 'r') as f:
            web = f.read()
        return web
    elif request.method == 'POST':
        print('request:')
        print(request.form)
        return 'POSTED'
    else:
        return 'not support method=[%s]'.format(request.method)

@app.route('/user/<user_id>', methods=['GET', 'POST', 'PUT'])
def user(user_id):
    # check user_id is valid, if not then return error message

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
        # FIXME put should not user default row
        row = userdatabase.get_default_row()

        row['id'] = user_id

        print('data=[{}]'.format(request.form))
        with userdatabase.UserDBWriter(db_path) as writer:
            writer.add_user(row)

        return 'user_id=[%s] updated=[%s]' % (user_id, json.dumps(row))

    else:
        return 'not support method=[%s]'.format(request.method)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



