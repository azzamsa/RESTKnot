from dnsagent.libs import control
from dnsagent.libs import utils
from dnsagent.libs import broker


def publish_status(**kwargs):
    status_code = kwargs.get("status_code")
    record_id = kwargs.get("record_id")
    cmd = kwargs.get("cmd")
    zone = kwargs.get("zone")
    item = kwargs.get("item")
    data = kwargs.get("data")
    knot_response = kwargs.get("knot_response")

    status = {
        "status": status_code,
        "process": {
            "record_id": record_id,
            "cmd": cmd,
            "zone": zone,
            "item": item,
            "data": data,
        },
        "knot_response": knot_response,
    }

    broker.send(status)


def execute(message, process):
    cmd = message.get("cmd")
    zone = message.get("zone")
    item = message.get("item")
    data = message.get("data")

    knot_response = control.send_block(
        cmd=cmd,
        section=message.get("section"),
        item=item,
        identifier=message.get("identifier"),
        zone=zone,
        owner=message.get("owner"),
        ttl=message.get("ttl"),
        rtype=message.get("rtype"),
        data=data,
        flags=message.get("flags"),
        filter_=message.get("filter"),
    )

    record_id = process["record_id"]
    status_code = "OK"
    if knot_response != "{}":
        status_code = "FAIL"
        utils.log_err(f"Failed: {knot_response}")

    publish_status(
        status_code=status_code,
        record_id=record_id,
        cmd=cmd,
        zone=zone,
        item=item,
        data=data,
        knot_response=str(knot_response),
    )
    utils.log_info(f"Created: {cmd} {zone or ''} {item or ''} {data or ''}")
