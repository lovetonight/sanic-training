import json
import uuid
from pymongo import MongoClient

from app.constants.mongodb_constants import MongoCollections
from app.models.book import Book
from app.models.user import User
from app.utils.logger_utils import get_logger
from config import MongoDBConfig

logger = get_logger('MongoDB')


class MongoDB:
    def __init__(self, connection_url=None):
        if connection_url is None:
            connection_url = f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'

        self.connection_url = f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'
        self.client = MongoClient(self.connection_url)
        self.db = self.client[MongoDBConfig.DATABASE]
        print("connection: ", self.connection_url)
        print("db: ", MongoDBConfig.DATABASE)

        self._books_col = self.db[MongoCollections.books]
        self._users_col = self.db[MongoCollections.users]
        
        
    # Books

    def get_books(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._books_col.find(filter_, projection=projection)
            data = []
            for doc in cursor:
                data.append(Book().from_dict(doc))
            return data
        except Exception as ex:
            logger.exception(ex)
        return []

    



    # TODO: write functions CRUD with books
    def get_book(self, book_id: str, projection=None):
        try:
            query = {'_id': book_id}
            print("query: ", query)
            cursor = self._books_col.find(query, projection=projection)
            print("cursor: ", cursor.count())
            return Book().from_dict(cursor[0])
        except Exception as ex:
            logger.exception(ex)
        return None
    
    
    def add_book(self, book: Book):
        try:
            inserted_doc = self._books_col.insert_one(book.to_dict())
            return inserted_doc
        except Exception as ex:
            logger.exception(ex)
        return None
    
    def create_book(self, body: dict, username: str):
        try:
            book_id = str(uuid.uuid4())
            book = Book(book_id).from_dict(body)
            book.owner = username
            
            
            inserted_doc = self._books_col.insert_one(book.to_dict())
            return inserted_doc
        except Exception as ex:
            logger.exception(ex)
        return None
    
    def delete_book(self, id: str):
        try:
            deletebook = self._books_col.delete_one({"_id":id})
            return True
        except Exception as ex:
            logger.exception(ex)
        return False
    
    
    def update_book(self, id:str, dict1: dict):
        try:
            result =self._books_col.update_many({"_id": id},{"$set":dict1})
            return result
        except Exception as ex:
            logger.exception(ex)
        return None

    # Users
    
    
    def get_user_by_username(self, username:str):
        try:
            query ={"username":username}
            cursor = self._users_col.find_one(query)
            return User().from_dict(cursor)
        except Exception as ex:
            logger.exception(ex)
        return None       
    def add_user(self, user:User):
        try:
            inserted_user = self._users_col.insert_one(user.to_dict())
            return inserted_user
        except Exception as ex:
            logger.exception(ex)
        return None                       