from flask import Flask, request, render_template, redirect
from utils.manager import ESPManager
from utils.controls import Controls
import json
import time


app = Flask(__name__)
controls = Controls({
    "D3": "switch 0 + onboard led",
    "D0": "switch 1",
    "D1": "switch 2",
    "D2": "switch 3",
    "D5": "switch 4",
    "D6": "switch 5",
    "D7": "switch 6",
    })

@app.route('/')
def index():
    return render_template("index.html", controls=controls, is_synced=controls.is_synced, request=request)

@app.route('/get')
def user_get_update():
    return json.dumps({k:{"value": v, "name": controls.switches[k]} for (k,v) in controls.mcu_state.items()})

@app.route('/set')
def user_set_update():
    controls.user_state.update(request.args)
    return redirect("/")

@app.route('/mcu-get-update')
def mcu_get_update():
    return json.dumps(controls.user_state)

@app.route('/mcu-set-update')
def mcu_set_update():
    controls.mcu_state.update(request.args)
    if not controls.is_synced:
        controls.user_state.update(request.args)
        controls.st = time.time()
        controls.synced = True
    return "ok"

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")