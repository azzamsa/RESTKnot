import yaml
import os

from app.models import model
from app.helpers import broker


def get_other_data(record_id):
    """Return other record data from given record id."""
    try:
        record = model.get_one(table="record", field="id", value=record_id)

        zone_id = record["zone_id"]
        type_id = record["type_id"]
        ttl_id = record["ttl_id"]

        zone = model.get_one(table="zone", field="id", value=zone_id)
        type_ = model.get_one(table="type", field="id", value=type_id)
        ttl = model.get_one(table="ttl", field="id", value=ttl_id)
        rdata = model.get_one(table="rdata", field="record_id", value=record_id)
        return (record, zone, type_, ttl, rdata)
    except Exception as error:
        raise ValueError(f"{error}")


def generate_command(**kwargs):
    """Return dictionary of given keywords & values."""
    zone = kwargs.get("zone_name")
    owner = kwargs.get("owner")
    rtype = kwargs.get("rtype")
    ttl = kwargs.get("ttl")
    rdata = kwargs.get("rdata")
    command = kwargs.get("command")

    cmd = {
        "cmd": command,
        "zone": zone,
        "owner": owner,
        "rtype": rtype,
        "ttl": ttl,
        "data": rdata,
    }

    return cmd


def set_config(zone, zone_id, command):
    """Send config command with JSON structure to broker."""

    # there are two option to put conf-begin and conf-commit
    # either here (api) or in (agent)
    # I'd rather choose to put it here for finer tuning
    conf_begin = {"cmd": "conf-begin", "zone": zone}
    conf_set = {"cmd": command, "section": "zone", "item": "domain", "data": zone}
    conf_commit = {"cmd": "conf-commit", "zone": zone}

    queries = []
    for query in [conf_begin, conf_set, conf_commit]:
        queries.append(query)

    # agent_type: master, slave
    # because config created both in  master and slave
    message = {
        "agent": {"agent_type": ["master", "slave"]},
        "process": {"zone": zone, "type": "config", "record_id": None},
        "knot": queries,
    }

    broker.send(message)


def set_zone(record_id, command):
    """Send zone command with JSON structure to broker."""
    record, zone, type_, ttl, rdata = get_other_data(record_id)
    zone_name = zone["zone"]

    zone_begin = {"cmd": "zone-begin", "zone": zone_name}
    zone_set = generate_command(
        zone=zone_name,
        owner=record["owner"],
        rtype=type_["type"],
        ttl=ttl["ttl"],
        rdata=rdata["rdata"],
        command=command,
    )
    zone_commit = {"cmd": "zone-commit", "zone": zone_name}

    queries = []
    for query in [zone_begin, zone_set, zone_commit]:
        queries.append(query)

    # agent_type: master
    # because zone only created in master, slave will get zone via axfr
    # zone: specify manual zone name, some knot operation don't return zone name
    message = {
        "agent": {"agent_type": ["master"]},
        "process": {"zone": zone_name, "type": "zone", "record_id": record_id},
        "knot": queries,
    }

    broker.send(message)


def set_default_zone(record_ids):
    """Send zone command with JSON structure to broker."""
    # We can use `send_zone` but it will be slow since each zone will be sent
    # separately

    zone_sets = []
    for record_id in record_ids:
        record, zone, type_, ttl, rdata = get_other_data(record_id)
        zone_name = zone["zone"]
        zone_set = generate_command(
            zone=zone_name,
            owner=record["owner"],
            rtype=type_["type"],
            ttl=ttl["ttl"],
            rdata=rdata["rdata"],
            command="zone-set",
        )
        zone_sets.append(zone_set)

    zone_begin = {"cmd": "zone-begin", "zone": zone_name}
    zone_commit = {"cmd": "zone-commit", "zone": zone_name}

    queries = []
    for query in [zone_begin, *zone_sets, zone_commit]:
        queries.append(query)

    # agent_type: master
    # because zone only created in master, slave will get zone via axfr
    message = {
        "agent": {"agent_type": ["master"]},
        "process": {"zone": zone_name, "type": "default-zone", "record_id": None},
        "knot": queries,
    }

    broker.send(message)


def cluster_file():
    """Return cluster file path."""
    path = os.environ.get("RESTKNOT_CLUSTER_FILE")
    if not path:
        raise ValueError(f"RESTKNOT_CLUSTER_FILE is not set")

    is_exists = os.path.exists(path)
    if is_exists:
        return path
    else:
        raise ValueError(f"Clustering File Not Found")


def get_clusters():
    """Return cluster file content."""
    file_ = cluster_file()
    clusters = yaml.safe_load(open(file_))
    return clusters


def delegate(zone, zone_id, command, agent_type):
    """Send delegation config command with JSON structure to broker."""
    clusters = get_clusters()
    cluster = clusters[agent_type]

    # default for master
    cluster_type = "notify"
    cluster_type_item = "notify"
    if agent_type == "slave":
        cluster_type = "master"
        cluster_type_item = "master"

    queries = [
        {"item": "file", "data": f"{zone}.zone", "identifier": zone},
        {"item": "serial-policy", "data": "dateserial"},
        {"item": "module", "data": "mod-stats/default"},
    ]
    queries.extend(
        [{"item": cluster_type_item, "data": item} for item in cluster[cluster_type]]
    )

    queries.extend([{"item": "acl", "data": acl} for acl in cluster["acl"]])

    queries_ = []
    for query in queries:
        query["cmd"] = command
        query["section"] = "zone"
        query["zone"] = zone
        queries_.append(query)

    message = {
        "agent": {"agent_type": [agent_type]},
        "process": {"zone": zone, "type": "delegate", "record_id": None},
        "knot": [{"cmd": "conf-begin"}, *queries_, {"cmd": "conf-commit"}],
    }

    broker.send(message)
