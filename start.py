import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify, send_file
from os import listdir,curdir
from os.path import isfile, join,getmtime
import os

app = Flask(__name__)
app.secret_key = 'h432hi5ohi3h5i5hi3o2hi'


@app.route('/')
def home():
    return render_template('home.html')




@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run()
