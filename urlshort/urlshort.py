import json
from urllib import request
from flask import Blueprint, url_for, render_template, request, redirect, flash, abort, session, jsonify
from werkzeug.utils import secure_filename
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

bp = Blueprint('urlshort', __name__)


@bp.route('/')
def home():
    return render_template('home.html', codes=session.keys())


@bp.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        urls = {}

        if os.path.exists('../urls.json'):
            with open('../urls.json') as urls_file:
                urls = json.load(urls_file)

        if request.form['code'] in urls.keys():
            flash('This shortname has already been taken')
            return redirect(url_for('urlshort.home'))

        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url': request.form['url']}
        else:
            f = request.files['file']
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save(f'{curr_dir}/static/user_files/{full_name}')
            urls[request.form['code']] = {'file': full_name}

        with open('../urls.json', 'w') as url_file:
            json.dump(urls, url_file)
            session[request.form['code']] = True

        return render_template('templates/your_url.html', code=request.form['code'])
    else:
        return redirect(url_for('urlshort.home'))


@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save(secure_filename(f.filename))


@bp.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('../urls.json'):
        with open('../urls.json') as urls_file:
            urls = json.load(urls_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename='user_files/' + urls[code]['file']))
    return abort(404)


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('templates/page_not_found.html'), 404


@bp.route('/api')
def api_root():
    return jsonify(list(session.keys()))
