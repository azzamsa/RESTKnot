from flask_restful import Resource, reqparse
from app.helpers.rest import response
from app.models import model
from app.libs import utils
from app.libs import validation
from app.middlewares import auth


def get_datum(data):
    if data is None:
        return

    results = []
    for d in data:
        datum = {"id": str(d["id"]), "zone": d["zone"], "user_id": d["user_id"]}
        results.append(datum)
    return results


class GetZoneData(Resource):
    @auth.auth_required
    def get(self):
        try:
            zones = model.get_all("zone")
        except Exception as e:
            return response(401, message=str(e))

        # FIXME do all user data needed?
        # users = model.get_by_id(table="user", field="id", user_id=user_id)
        data = get_datum(zones)
        return response(200, data=data)


class GetZoneDataId(Resource):
    @auth.auth_required
    def get(self, zone_id):
        try:
            zone = model.get_by_id(table="zone", field="id", id_=zone_id)
        except Exception as e:
            return response(401, message=str(e))
        else:
            # FIXME do all user data needed?
            # user_data = model.get_by_id("user", data_zone["user"])
            data = get_datum(zone)
            return response(200, data=data)


class ZoneAdd(Resource):
    @auth.auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("user_id", type=str, required=True)
        parser.add_argument("zone", type=str, required=True)
        args = parser.parse_args()
        zone = args["zone"].lower()
        user_id = args["user_id"]

        # FIXME why this still needed? we already had user_id?
        # user = model.get_user_by_project_id(user_id)["zone_id"]
        # user = model.get_user_by_project_id(user_id)
        zone_id = utils.get_last_key("zone")
        print(zone_id)

        if utils.check_unique("zone", "value", zone):
            return response(401, message="Duplicate zone Detected")

        if validation.zone_validation(zone):
            return response(401, message="Named Error")

        data = {"zone": zone, "user_id": user_id}
        try:
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
        parser.add_argument("user_id", type=str, required=True)
        args = parser.parse_args()
        zone = args["zone"].lower()

        if utils.check_unique("zone", "zone", zone, key=zone_id):
            return response(401, message="Duplicate zone Detected")
        if validation.zone_validation(zone):
            return response(401, message="Named Error")

        data = {
            "where": {"id": zone_id},
            "data": {"zone": args["zone"], "user_id": args["user_id"]},
        }
        try:
            model.update("zone", data=data)
        except Exception as e:
            return response(401, message=str(e))
        else:
            return response(200, data=data, message="Edited")


class ZoneDelete(Resource):
    @auth.auth_required
    def delete(self, zone_id):
        try:
            data = model.delete(table="zone", field="id", value=zone_id)
        except Exception as e:
            return response(401, message=str(e))
        else:
            # FIXME still say 'deleted' even data = 0
            return response(200, data=data, message="Deleted")
