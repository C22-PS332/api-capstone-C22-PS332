import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_UNAME = os.getenv("DB_UNAME")
DB_PW = os.getenv("DB_PW")
DB_IP = os.getenv("DB_IP")
SPOON_API_KEY = os.getenv("SPOON_API_KEY")

connectionString = "mysql://{uname}:{pw}@{ip}:3306/user".format(uname=DB_UNAME, pw=DB_PW, ip=DB_IP)

print(connectionString)