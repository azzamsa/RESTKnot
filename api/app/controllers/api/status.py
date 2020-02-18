from flask import request
from flask_restful import Resource, reqparse
from app.vendors.rest import response
from app.models import model
from app.middlewares import auth
from app.helpers import broker


class StatusList(Resource):
    @auth.auth_required
    def get(self):
        try:
            messages = broker.take_message()

            if not messages:
                return response(404)

            return response(200, data=messages)
        except Exception as e:
            print(e)
            return response(500)


class Status(Resource):
    @auth.auth_required
    def get(self):
        try:
            return response(200)
        except Exception:
            return response(500)
