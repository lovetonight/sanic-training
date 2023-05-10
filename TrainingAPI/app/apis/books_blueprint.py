import uuid
from sanic import Blueprint
from sanic.response import json

from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB
from app.databases.redis_cached import get_cache, set_cache
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError
from app.models.book import create_book_json_schema, Book
from app.decorators.auth import protected

books_bp = Blueprint("books_blueprint", url_prefix="/books")

_db = MongoDB()


def find_book(books, book_id):
    for book in books:
        if book["_id"] == book_id:
            return book
    return None


def update_books_by_id(books, book_id, book_obj):
    for i, book in enumerate(books):
        if book["_id"] == book_id:
            books[i] = book_obj.to_dict()
            return books
    return books


def delete_books_by_id(books, book_id):
    new_books = []
    for book in books:
        if book["_id"] != book_id:
            new_books.append(book)
    return new_books


@books_bp.route("/")
async def get_all_books(request):
    # # TODO: use cache to optimize api
    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
            await set_cache(r, CacheConstants.all_books, books)

    # book_objs = _db.get_books()
    # books = [book.to_dict() for book in book_objs]
    number_of_books = len(books)
    return json({"n_books": number_of_books, "books": books})


# Create new book


@books_bp.route("/", methods={"POST"})
@protected  # TODO: Authenticate
@validate_with_jsonschema(create_book_json_schema)  # To validate request body
async def create_book(request, username=None):
    body = request.json

    book_id = str(uuid.uuid4())
    book = Book(book_id).from_dict(body)
    book.owner = username
    inserted = _db.add_book(book)
    if not inserted:
        raise ApiInternalError("Fail to create book")

    # TODO: Update cache
    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
        else:
            books.append(book.to_dict())
        # Set book object in Redis cache
        async with request.app.ctx.redis as r:
            await set_cache(r, CacheConstants.all_books, books)

    return json({"status": "success"})


# TODO: write api get, update, delete book


# DELETE book
@books_bp.route("<book_id:str>", methods={"DELETE"})
@protected
async def delete_book(request, book_id, username=None):
    book_obj = _db.get_book(book_id)
    if not book_obj:
        raise ApiInternalError("Book not found")

    if book_obj.owner != username:
        raise ApiInternalError("User does not have permission to delete book")

    # Delete book from database
    result = _db.delete_book(book_id)
    if not result:
        raise ApiInternalError("Fail to delete book")

    # TODO: Update cache
    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
        else:
            books = delete_books_by_id(books, book_id)
        # Set book object in Redis cache
        async with request.app.ctx.redis as r:
            await set_cache(r, CacheConstants.all_books, books)

    return json({"status": "success"})


# Update Book


@books_bp.route("<book_id:str>", methods={"PUT"})
@protected
async def update_book(request, book_id, username=None):
    body = request.json
    book_obj = _db.get_book(book_id)

    if not book_obj:
        raise ApiInternalError("Book not found")

    if book_obj.owner != username:
        raise ApiInternalError("User does not have permission to modify book")

    # Update book in database
    updated = _db.update_book(book_id, body)
    if not updated:
        raise ApiInternalError("Fail to update book")

    # TODO: update cache

    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
            # books = update_books_by_id(books, book_id, book_obj)
            # await set_cache(r, CacheConstants.all_books, books)
        else:
            books = update_books_by_id(books, book_id, book_obj)
        # Set book object in Redis cache
        async with request.app.ctx.redis as r:
            await set_cache(r, CacheConstants.all_books, books)

    return json({"status": "success"})


# Read Book
@books_bp.route("<book_id:str>", methods={"GET"})
async def get_book(request, book_id):
    # Use cache to optimize api
    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
            await set_cache(r, CacheConstants.all_books, books)
            book_obj = find_book(books, book_id)
            return json(book_obj.to_dict())

        book_obj = find_book(books, book_id)

        # Book not found in cache, fetch it from database
        if not book_obj:
            book_obj = _db.get_book_by_id(book_id)
            if not book_obj:
                raise ApiInternalError("Book not found")
            books.append(book_obj.to_dict())
            await set_cache(r, CacheConstants.all_books, books)
            return json(book_obj.to_dict())

        return json(book_obj)
