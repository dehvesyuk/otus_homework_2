import datetime
import hashlib
import json
import functools
import logging
import uuid
from typing import List
from http.server import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser

from fields import (
    ClientIDsField, DateField, CharField, EmailField, PhoneField, BirthDayField,
    GenderField, ArgumentsField
)
from scoring import get_interests

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Request:
    def __init__(self, **params):
        for key, value in params.items():
            setattr(self, key, value)
        self.validate()



class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def validate(self):
        # TODO add try: except block with raise
        return self._client_ids != []

    @property
    def context(self):
        return {
            "nclients": len(self._client_ids)
        }

    def generate_response(self):
        return get_interests({}, self._client_ids)


class OnlineScoreRequest:
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest:
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(
            datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def login_required(method_handler: callable):
    @functools.wraps(method_handler)
    def wrapper(request: MethodRequest, ctx, store):
        if check_auth(request):
            res = method_handler(request, ctx, store)
        else:
            res = (FORBIDDEN, ERRORS[FORBIDDEN])
        return res
    return wrapper


def method_handler(request, ctx, store):
    response, code = None, None
    return response, code


def clients_interests_handler(request, ctx, store):
    logging.info(f"request: {request}, ctx: {ctx}, store: {store}")
    #TODO add auth decorator
    handler = ClientsInterestsRequest(request["body"])
    context = handler.context
    response = handler.generate_response()
    try:
        handler.validate()
        return response, 200
    except Exception as e:
        return {"error": f"ошибка валидации, {e}"}, 422


def online_score_handler(request, ctx, store):
    #TODO add handler and auth decorator
    response, code = None, None
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "clients_interests": clients_interests_handler,
        "online_score": online_score_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (
                self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers},
                        context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {
                "error": response or ERRORS.get(code, "Unknown Error"),
                "code": code
            }
        logging.info(f"r object: {r}")
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
