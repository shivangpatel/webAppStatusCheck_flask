import json
import threading
from multiprocessing.dummy import Pool as ThreadPool
from socket import gaierror, gethostbyname
from time import gmtime, strftime, time
from urllib.parse import urlparse

import requests
from flask import Flask, render_template, request, escape, jsonify
from flask_mail import Mail, Message

from settings import refresh_interval, filename, site_down, number_threads, include_search, MAIL_SERVER, MAIL_PASSWORD, \
    MAIL_PORT, MAIL_USERNAME, MAIL_USE_SSL, MAIL_USE_TLS, NOTIFICATION_RECIEVED_BY, MAIL_SUBJECT

lastDictUpdate = {}


def is_reachable(url):
    """ This function checks to see if a host name has a DNS entry
    by checking for socket info."""
    try:
        gethostbyname(url)
    except gaierror:
        return False
    else:
        return True


def get_status_code(url):
    """ This function returns the status code of the url."""
    try:
        status_code = requests.get(url, timeout=30).status_code
        if status_code != 200:
            tmp_time = time()
            if url in lastDictUpdate:
                if lastDictUpdate[str(url)] < tmp_time or lastDictUpdate[str(url)] == site_down:
                    lastDictUpdate[str(url)] = tmp_time + 60  # 15min = 900 seconds
                    siteDownNotification(url, status_code)
                    print(lastDictUpdate)
            else:
                lastDictUpdate[str(url)] = tmp_time + 60
                siteDownNotification(url, status_code)
        return status_code
    except requests.ConnectionError:
        if url in lastDictUpdate:
            tmp_time = time()
            if lastDictUpdate[str(url)] < tmp_time or lastDictUpdate[str(url)] == site_down:
                lastDictUpdate[str(url)] = tmp_time + 60  # 15min = 900 seconds
                siteDownNotification(url, site_down)
                print(lastDictUpdate)
        else:
            tmp_time = time()
            lastDictUpdate[str(url)] = tmp_time + 60
            siteDownNotification(url, site_down)
            print(lastDictUpdate)
        return site_down


def check_single_url(url):
    """This function checks a single url and if connectable returns
    the status code, else returns variable site_down (default: UNREACHABLE)."""
    if is_reachable(urlparse(url).hostname) == True:
        return str(get_status_code(url))
    else:
        return site_down


def launch_checker():
    """This function launches the check_multiple_urls function every x seconds
    (defined in refresh interval variable)."""
    t = threading.Timer(refresh_interval, launch_checker)
    t.daemon = True
    t.start()
    global returned_statuses
    returned_statuses = check_multiple_urls()
    print(returned_statuses)


def check_multiple_urls():
    """This function checks through urls specified in the checkurls.json file
    (specified in the filename variable) and
    returns their statuses as a dictionary."""
    statuses = {}
    temp_list_statuses = []
    global last_update_time
    pool = ThreadPool(number_threads)
    temp_list_statuses = pool.map(check_single_url, list_urls)
    for i in range(len(list_urls)):
        statuses[list_urls[i]] = temp_list_statuses[i]
    last_update_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return statuses


def compare_submitted(submitted):
    """This function checks whether the value in the dictionary is found in 
    the checkurls.json file. """
    stripped_submission = https_start_strip(submitted)
    if stripped_submission in list_urls:
        flaggy = True
    else:
        flaggy = False
    return (flaggy, stripped_submission)


def https_start_strip(url):
    url = url.strip().lower()
    if url[:7] == 'http://':
        return url
    elif url[:8] == 'https://':
        return url
    else:
        url = "https://" + url
        return url


def generate_list_urls(input_dict):
    list_urls = []
    for group, urls in input_dict.items():
        for url in urls:
            list_urls.append(url)
    return list_urls


app = Flask(__name__)
mail = Mail(app)  # instantiate the mail class

# configuration of mail
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
mail = Mail(app)

msg = Message(
    MAIL_SUBJECT,
    sender= MAIL_USERNAME,
    recipients= NOTIFICATION_RECIEVED_BY
)


def siteDownNotification(url, status_code):
    msg.body =  str(url) + ' ---> is Down '
    with app.app_context():
        mail.send(msg)
        # call your method here
    print(url)
    print(status_code)
    # return 'Mail Sent !'


@app.route("/", methods=["GET"])
def display_returned_statuses():
    return render_template(
        'index.html',
        returned_statuses=returned_statuses,
        checkurls=checkurls,
        last_update_time=last_update_time,
        include_search=include_search
    )


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        results = compare_submitted(escape(request.form['submitted']))
        return render_template(
            'index.html',
            results=results,
            returned_statuses=returned_statuses,
            checkurls=checkurls,
            last_update_time=last_update_time
        )


@app.route("/api", methods=["GET"])
def display_returned_api():
    return jsonify(
        returned_statuses
    ), 200


with open(filename) as f:
    checkurls = json.load(f)
list_urls = generate_list_urls(checkurls)
returned_statuses = {}
last_update_time = 'time string'

if __name__ == '__main__':
    launch_checker()
    app.run()
