import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from secret import DB_UNAME, DB_IP, DB_PW
# engine = sqlalchemy.create_engine("postgresql://admin:admin@localhost:5432/user")
# engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root:123@db-mariadb:3306/user")
# engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root@localhost:3306/user")
connectionString = "mysql://{uname}:{pw}@{ip}:3306/user".format(uname=DB_UNAME, pw=DB_PW, ip=DB_IP)
engine = sqlalchemy.create_engine(connectionString)
# engine = sqlalchemy.create_engine("postgresql://xpjfchbo:urdE0vW2Q8Q9iVYuX6-DGmundndpKKBc@rosie.db.elephantsql.com/xpjfchbo")
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try :
        yield db
    except :
        db.close()