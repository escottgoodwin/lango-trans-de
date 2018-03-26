import json
from flask import Flask, flash, redirect, render_template, request, session, abort
import webbrowser,threading

app = Flask(__name__)

link_recs = json.load(open('link_recs_20180323161114442598.txt'))

@app.route("/")
def index():
    return render_template(
        'cold_start2.html',link_recs=link_recs)


if __name__ == "__main__":
    app.debug = True
    threading.Timer(1.25, lambda: webbrowser.open('http://127.0.0.1:5084/')).start()
    app.run(port=5084)
