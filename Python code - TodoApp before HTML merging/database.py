from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite3
#
#SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db" # Initialize the name of db store in the system.
#
#engine = create_engine(
#    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
#)
#
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
## Create Base, Allow to create model
#Base = declarative_base()

# PostgreSQL
#
#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:welcome2WDC@localhost/TodoApplicationDatabase" # Initialize the name of db store in the system.
#
#engine = create_engine(SQLALCHEMY_DATABASE_URL)
#
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
##eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJGbGludCIsImlkIjoxLCJleHAiOjE2NDcxMTQxNTJ9.zXUQuG34JaEbCoknJAw1B8uy7sAZBsg8LlhanjI2OWQ
##eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJFeGFtcGxlIiwiaWQiOjIsImV4cCI6MTY0NzExNDE4N30.e4hH__cgR-1GIXo0wCjeUJkIUKI30b7QrGDISFPc8Bs
## Create Base, Allow to create model
#Base = declarative_base()

# MySQL
#
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:welcome2WDC@127.0.0.1:3306/todoapp" # Initialize the name of db store in the system.
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhIiwiaWQiOjEsImV4cCI6MTY0NzEyMjgzOX0.KGddPf3BSA8k1BBcd_S_X2nafR3DehvqZ6l_pQdjlkk
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiIiwiaWQiOjIsImV4cCI6MTY0NzEyMjg2Mn0.xohCHsqekcpxxv4hrC1qnjAiNhI75ZK3rNgeH77aEyY
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base, Allow to create model
Base = declarative_base()