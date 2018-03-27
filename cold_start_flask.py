import json
from flask import Flask, flash, redirect, render_template, request, session, abort
import webbrowser,threading

def start_flask(link_recs):

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template(
            'cold_start2.html',saved_recs=link_recs)


    threading.Timer(1.25, lambda: webbrowser.open('http://127.0.0.1:5084/')).start()
    app.run(port=5084)

if __name__ == "__main__":

    saved_recs = json.load(open('link_recs.txt'))
    start_flask(saved_recs)
