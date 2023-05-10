from flask import Flask, render_template, request
from dotenv import load_dotenv
from flask_caching import Cache
import logging
import os 
import time
import requests
import json
import pynetbox
import paramiko

load_dotenv() 

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# Creates Flask Application 
app = Flask(__name__)
checked_values = []
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


# Restart function
def restart(host):
    special_account = os.getenv('PPC_LOGIN')
    client = paramiko.SSHClient()
    policy = paramiko.AutoAddPolicy()
    client.set_missing_host_key_policy(policy)
    client.connect(host, username=special_account, password=os.getenv('PPC_PASSWORD'))
    _stdin,_stdout,_stderr = client.exec_command("systemctl --user restart onair-electron") # Command to execute
    print(_stdout.read().decode())
    client.close
    return host

# Stop function  
def stop(host):

    special_account = os.getenv('PPC_LOGIN')
    client = paramiko.SSHClient()
    policy = paramiko.AutoAddPolicy()
    client.set_missing_host_key_policy(policy)
    client.connect(host, username=special_account, password=os.getenv('PPC_PASSWORD'))
    _stdin,_stdout,_stderr = client.exec_command("systemctl --user stop onair-electron") # Command to execute
    print(_stdout.read().decode())
    client.close
    return host


@cache.cached(timeout=60)
def get_ppcs_list():
    t = time.time()
    device_dict = {'label': '', 'name': '', 'id': ''}
    device_list = []
    nb = pynetbox.api(
        'https://netbox.onairent.live',
        token= os.getenv('NETBOX_TOKEN')
    )
    # Define tags and netbox filter properties
    devices = nb.dcim.devices.filter(tag='prod_ppc', site='lv01',status='active')

    for device in devices:
        new_device_dict = device_dict.copy()
        new_device_dict['label'] = device.name
        new_device_dict['name'] = device.name + '.int.onairent.live'
        new_device_dict['id'] = device.name + '.int.onairent.live'
        device_list.append(new_device_dict)
        device_dict.clear()
    print('API Load Time\nElapsed: %.3f seconds' % (time.time() - t))
    return device_list

def meme():
    url = "https://meme-api.com/gimme"
    nsfw = True
    response = json.loads(requests.request("GET", url).text)
    meme_large = response["preview"][-2]
    subreddit = response["subreddit"]
    return meme_large, subreddit

@app.route("/update_checked_values", methods=["POST"])
def update_checked_values():
    global checked_values
    checked_values = request.get_json()['checkedValues']
    return "OK"

@app.route('/', methods=["POST", "GET"])
def index():
    start = time.time()
    items = get_ppcs_list()
    if "restart_btn2" in request.form:
        for value in checked_values: #list of strings
            print("restarting - {}".format(value))
            restart(value)
            
    if 'stop_btn1' in request.form:
        for value in checked_values: #list of strings
            print("restarting - {}".format(value))
            stop(value)
    print('Page load time\nElapsed: %.3f seconds' % (time.time() - start))
    return render_template('telo.html', items=items)
    

@app.route('/meme')
def meme_get():
    meme_pic,subreddit = meme()
    return render_template("meme.html", meme_pic=meme_pic, subreddit=subreddit)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")