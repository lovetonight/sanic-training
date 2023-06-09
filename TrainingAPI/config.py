import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    RUN_SETTING = {
        'host': os.environ.get('SERVER_HOST', '0.0.0.0'),
        'port': int(os.environ.get('SERVER_PORT', 1221)),
        'debug': False,
        "access_log": True,
        "auto_reload": True,
        'workers': 1
    }
    # uWSGI를 통해 배포되어야 하므로, production level에선 run setting을 건드리지 않음

    SECRET_KEY = os.getenv('SECRET_KEY', '85c145a16bd6f6e1f3e104ca78c6a102')
    EXPIRATION_JWT = 3600  # seconds

    REDIS = 'redis://localhost:6379/0'


class LocalDBConfig:
    pass


class RemoteDBConfig:
    pass


class MongoDBConfig:
    USERNAME = os.environ.get("MONGO_USERNAME") or "lovetonight"
    PASSWORD = os.environ.get("MONGO_PASSWORD") or "hoandt"
    HOST = os.environ.get("MONGO_HOST") or "localhost"
    PORT = os.environ.get("MONGO_PORT") or "27027"
    DATABASE = os.environ.get("MONGO_DATABASE") or "hoandt"
