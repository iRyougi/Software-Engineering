from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, jsonify, flash
from flask_mail import Mail, Message
import mysql.connector
import os
import random
import base64
import pandas as pd
from io import BytesIO
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
import pandas as pd

from Email.views import email_bp
from User.views import user_bp
from Data_User.views import datauser_bp
from service.views import service_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Flask-Mail配置
app.config['MAIL_SERVER'] = 'smtp.exmail.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 's230026238@mail.uic.edu.cn'
app.config['MAIL_PASSWORD'] = 'Swjp@#(97=k'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# ========== 各个模块的路由合并 ==========

# ==== User模块，路由加前缀 /user ====
app.register_blueprint(user_bp, url_prefix='/user')

# ==== Data User模块，路由加前缀 /datauser ====
app.register_blueprint(datauser_bp, url_prefix='/datauser')

# ==== Service模块，路由加前缀 /service ====
app.register_blueprint(service_bp, url_prefix='/')

# ========== Email模块路由，全部加 /email 前缀 ==========
app.register_blueprint(email_bp, url_prefix='/email')\


#Debug
print(app.url_map) #打印出所有注册的 endpoint

# ========== 启动 ==========
if __name__ == '__main__':
    app.run(debug=True)
    print(app.url_map)