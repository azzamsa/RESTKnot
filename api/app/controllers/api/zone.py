from flask_restful import Resource, reqparse
from app.helpers.rest import response
from app.helpers import helpers
from app.models import model
from app.helpers import validator
from app.middlewares import auth


class GetZoneData(Resource):
    @auth.auth_required
    def get(self):
        try:
            zones = model.get_all("zone")
            return response(200, data=zones)
        except Exception as e:
            return response(401, message=str(e))


class GetZoneDataId(Resource):
    @auth.auth_required
    def get(self, zone_id):
        try:
            zone = model.get_one(table="zone", field="id", value=zone_id)
            zone = helpers.exclude_keys(zone, {"is_committed"})
            return response(200, data=zone)
        except Exception as e:
            return response(401, message=str(e))


class ZoneAdd(Resource):
    @auth.auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("zone", type=str, required=True)
        parser.add_argument("project_id", type=str, required=True)
        args = parser.parse_args()
        zone = args["zone"].lower()
        project_id = args["project_id"]

        if not model.is_unique(table="zone", field="zone", value=f"{zone}"):
            return response(401, message="Duplicate zone Detected")

        try:
            validator.validate("ZONE", zone)
        except Exception as e:
            return response(401, message=str(e))

        # FIXME "is_committed" should be added
        try:
            user_id = user_model.user_id_by_project(project_id)

            data = {"zone": zone, "user_id": user_id}
            model.insert(table="zone", data=data)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Inserted")


class ZoneEdit(Resource):
    @auth.auth_required
    def put(self, zone_id):
        parser = reqparse.RequestParser()
        parser.add_argument("zone", type=str, required=True)
        parser.add_argument("project_id", type=str, required=True)
        args = parser.parse_args()
        zone = args["zone"].lower()
        project_id = args["project_id"]

        if not model.is_unique(table="zone", field="zone", value=f"{zone}"):
            return response(401, message="Duplicate zone Detected")

        try:
            validator.validate("ZONE", zone)
        except Exception as e:
            return response(401, message=str(e))

        try:
            user_id = user_model.user_id_by_project(project_id)

            data = {
                "where": {"id": zone_id},
                "data": {"zone": args["zone"], "user_id": user_id},
            }
            model.update("zone", data=data)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data.get("data"), message="Edited")


class ZoneDelete(Resource):
    @auth.auth_required
    def delete(self, zone_id):
        try:
            data = model.delete(table="zone", field="id", value=zone_id)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Deleted")
