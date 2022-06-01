from flask import Flask, request, render_template, redirect
from flask_cors import CORS
from collections import defaultdict
from utils.device import ESPDevice
from threading import Lock
import json
import time

app = Flask(__name__)
CORS(app)
devices = defaultdict(dict)
lock = Lock()

######################## User endpoints #######################
def get_num_active_devices():
    total_active = 0
    inactive_auth_tokens = []
    inactive_devices = []
    for auth_token in devices:
        active = 0
        for device_id, device in devices[auth_token].items():
            total_active += int(device.synced)
            active += int(device.synced)
            if not device.synced:
                inactive_devices.append((auth_token, device_id))

        if active == 0:
            inactive_auth_tokens.append(auth_token)
    
    for (auth_token, device_id) in inactive_devices:
        try: del devices[auth_token][device_id]
        except: pass

    for auth_token in inactive_auth_tokens:
        # delete user account if no devices are connected
        try: del devices[auth_token]
        except: pass
    
    return total_active

@app.route('/')
def index():
    auth_token = request.args.get('auth', None)
    device_id = request.args.get('device-id', None)
    pin = request.args.get('update', None)
    if pin:
        pin, state = pin.split("=")
        devices[auth_token][device_id].user_state.update({pin:state})
        return {"message": "ok"}
    
    num_devices = get_num_active_devices()
    
    if not auth_token:
        return render_template("index.html", num_devices=num_devices)
    else:
        return render_template("devices.html", request=request, auth_token=auth_token, devices=devices, device_id=device_id, num_devices=num_devices)

@app.route("/get-devices")
def get_devices():
    auth_token = request.args.get("auth", None)
    if not auth_token: return {"message": "Auth Token missing!"}, 401
    device_ids = devices.get(auth_token, None)
    if not device_ids: return {"message": "No devices found"}, 400
    return json.dumps(list(device_ids.keys()))

@app.route("/get-update")
def get_update():
    auth_token = request.args.get("auth", None)
    device_id = request.args.get("device-id", None)
    device = devices.get(auth_token, {}).get(device_id, None)
    if not auth_token: return {"message": "Auth Token missing!"}, 401
    if not device_id: return {"message": "Device ID missing!"}, 401    
    if not device: return {"message": "No device found"}, 400
    return json.dumps(device.mcu_state)

######################## MCU endpoints #######################
def parse_header(header):
    auth_token = header.get('auth_token', None)
    device_id = header.get('device_id', None)
    labels = header.get('labels', None)
    return [auth_token, device_id, labels]

@app.route('/mcu-get-update')
def mcu_get_update():
    auth_token, device_id, labels = parse_header(request.headers)
    if None in [auth_token, device_id, labels]:
        return {"message": "incorrect data"}, 400

    if device_id not in devices[auth_token]:
        device = ESPDevice(labels, request.headers.get('alias', None))
        devices[auth_token][device_id] = device
    else:
        device = devices[auth_token][device_id]
    return device.user_state

@app.route('/mcu-set-update', methods=['POST'])
def mcu_set_update():
    auth_token, device_id, labels = parse_header(request.headers)
    if None in [auth_token, device_id, labels]:
        return {"message": "incorrect data"}, 400
    
    if device_id not in devices[auth_token]:
        device = ESPDevice(labels, request.headers.get('alias', None))
        devices[auth_token][device_id] = device
    else:
        device = devices[auth_token][device_id]
    
    with lock:
        if not device.is_synced:
            device.sync_state(request.json)
    
    return "ok"

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")