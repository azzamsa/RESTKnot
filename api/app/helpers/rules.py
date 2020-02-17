#  --------------------------------------------------------------------
# DNS Rules
#
# The rules for DNS records:
#
# CNAME
# 1. same owner NOT allowed
# 2. owner CAN'T coexist with the same A owner
#
# A
# 1. same owner allowed
# 2. owner CAN'T coexist with the same CNAME owner
# --------------------------------------------------------------------

from app.models import rules as rules_model
from app.models import type_ as type_model


def is_allowed_cname(zone_id, type_id, owner, rdata):
    #  duplicate record NOT allowed
    rules = rules_model.Rules()
    rules.is_duplicate(zone_id, type_id, owner, rdata)

    # 1. same owner NOT allowed
    query = '"type_id"=%(type_id)s AND "owner"=%(owner)s'
    value = {"zone_id": zone_id, "type_id": type_id, "owner": owner}
    rules = rules_model.Rules(query, value)

    is_unique = rules.is_unique()
    if not is_unique:
        raise ValueError("A CNAME record already exist with that owner")

    # 2. owner CAN'T coexist with the same A owner
    a_type_id = type_model.get_typeid_by_rtype("A")
    query = '"type_id" IN (%(type1)s,%(type2)s) AND "owner"=%(owner)s'
    value = {"zone_id": zone_id, "type1": type_id, "type2": a_type_id, "owner": owner}
    rules = rules_model.Rules(query, value)

    is_coexist = rules.is_coexist()
    if is_coexist:
        raise ValueError("An A record already exist with that owner")


def is_allowed_a(zone_id, type_id, owner, rdata):
    #  duplicate record NOT allowed
    rules = rules_model.Rules()
    rules.is_duplicate(zone_id, type_id, owner, rdata)

    # 2. owner CAN'T coexist with the same CNAME owner
    cname_type_id = type_model.get_typeid_by_rtype("CNAME")
    query = '"type_id"=%(type_id)s AND "owner"=%(owner)s'
    value = {"zone_id": zone_id, "type_id": cname_type_id, "owner": owner}
    rules = rules_model.Rules(query, value)

    is_coexist = rules.is_coexist()
    if is_coexist:
        raise ValueError("A CNAME record already exist with that owner")


def is_allowed_cname_edit(zone_id, type_id, owner, record_id):
    # 1. same owner NOT allowed

    # owner not needed cause same owner already
    # rejected in `add` operation
    query = '"type_id"=%(type_id)s AND "owner"=%(owner)s AND "id"<>%(record_id)s'
    value = {
        "zone_id": zone_id,
        "type_id": type_id,
        "owner": owner,
        "record_id": record_id,
    }
    rules = rules_model.Rules(query, value)

    is_unique = rules.is_unique()
    if not is_unique:
        raise ValueError("A CNAME record already exist with that owner")

    # 2. owner CAN'T coexist with the same A owner
    a_type_id = type_model.get_typeid_by_rtype("A")
    query = '"type_id" IN (%(type1)s,%(type2)s) AND "owner"=%(owner)s AND "id"<>%(record_id)s'
    value = {
        "zone_id": zone_id,
        "type1": type_id,
        "type2": a_type_id,
        "owner": owner,
        "record_id": record_id,
    }
    rules = rules_model.Rules(query, value)

    is_coexist = rules.is_coexist()
    if is_coexist:
        raise ValueError("An A record already exist with that owner")


# function based on rtype input when adding record
functions_add = {"CNAME": is_allowed_cname, "A": is_allowed_a, "AAAA": is_allowed_a}
functions_edit = {
    "CNAME": is_allowed_cname_edit,
    "A": is_allowed_a,
    "AAAA": is_allowed_a,
}


def check_add(rtype, zone_id, type_id, owner, rdata):
    rtype = rtype.upper()
    if rtype in functions_add.keys():
        functions_add[rtype](zone_id, type_id, owner, rdata)


def check_edit(rtype, zone_id, type_id, owner, record_id=None):
    rtype = rtype.upper()
    if rtype in functions_edit.keys():
        functions_edit[rtype](zone_id, type_id, owner, record_id)
