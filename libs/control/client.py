import json, os

def sendblock(ctl,params):

    try:
        cmd= params['cmd']
    except Exception as e:
        print("CMD Parameters needed")

    try:
        pass
    except Exception:
        pass

    try:
        section = params['section']
    except Exception:
        section=None

    try:
        item = params['item']
    except Exception:
        item=None

    try:
        identifier = params['identifier']
    except Exception:
        identifier=None

    try:
        zone = params['zone']
    except Exception:
        zone=None

    try:
        owner = params['owner']
    except Exception:
        owner=None

    try:
        ttl = params['ttl']
    except Exception:
        ttl=None

    try:
        rtype = params['rtype']
    except Exception:
        rtype=None

    try:
        data = params['data'][0]
        data = str(data)
    except Exception:
        data=None

    try:
        flags = params['flags']
    except Exception:
        flags=None

    try:
        filters = params['filter']
    except Exception:
        filters=None

    ctl.send_block(cmd, section=section, item=item, identifier=identifier, zone=zone,
                   owner=owner, ttl=ttl, rtype=rtype, data=data, flags=flags,
                   filter=filters)


