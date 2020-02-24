from flask import request
from flask_restful import Resource, reqparse
from app.vendors.rest import response
from app.models import model
from app.middlewares import auth
from app.helpers import broker
from kafka import TopicPartition


class StatusList(Resource):
    @auth.auth_required
    def get(self):
        try:
            messages = []
            consumer = broker.kafka_consumer(topic="status")

            for message in consumer:
                messages.append(message.value)

            consumer.close()

            if not messages:
                return response(404)

            return response(200, data=messages)
        except Exception as e:
            print(e)
            return response(500)


class Status(Resource):
    @auth.auth_required
    def get(self):
        start = request.args.get("start", 0)
        end = request.args.get("end", 10)
        status = request.args.get("status")
        cmd = request.args.get("cmd")
        record_id = request.args.get("rId")
        process_type = request.args.get("type")
        zone = request.args.get("zone")

        try:
            consumer = broker.kafka_consumer_no_topic()
            partition = TopicPartition("status", 0)
            consumer.assign([partition])
            consumer.seek(partition, int(start))

            messages = []

            for msg in consumer:
                if msg.offset > int(end):
                    break

                msg_value = msg.value
                # if (
                #     msg_value["status"] == status
                #     and msg_value["process"]["cmd"] == cmd
                #     and msg_value["process"]["record_id"] == record_id
                #     and msg_value["process"]["type"] == process_type
                #     and msg_value["process"]["zone"] == zone
                # ):

                if process_type and zone:
                    if (
                        msg_value["process"]["type"] == process_type
                        and msg_value["process"]["zone"] == zone
                    ):
                        messages.append(msg_value)
                if process_type and zone and cmd:
                    if (
                        msg_value["process"]["cmd"] == cmd
                        and msg_value["process"]["type"] == process_type
                        and msg_value["process"]["zone"] == zone
                    ):
                        messages.append(msg_value)

                else:
                    messages.append(msg_value)

            consumer.close()

            if not messages:
                return response(404)

            return response(200, data=messages)
        except Exception as e:
            print(e)
            return response(500)
