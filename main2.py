from pymysqlpool.pool import Pool
import os
from os.path import join, dirname
from dotenv import load_dotenv

import time

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
db_host = os.environ.get("DB_HOST")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")

pool = Pool(host=db_host, port=3306, user=db_user, password=db_password, db=db_name,autocommit=True,ping_check=True)

connection_db = pool.get_conn()
time.sleep(700)