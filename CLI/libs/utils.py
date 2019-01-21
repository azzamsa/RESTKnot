import json
import requests
import datetime
import tabulate
import coloredlogs
import logging
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt




with open('libs/templates/var.json','r') as f :
    var_json = json.load(f)


def check_existence(endpoint,var):
    url = get_url(endpoint)
    key = var_json['key'][endpoint]

    result = requests.get(url)
    result = result.json()
    result = result['data']
    for i in result:
        if i[key] == var:
            respons = True
            break
        else :
            respons = False
    return respons

def get_url(endpoint):
    url = "http://127.0.0.1:6968/api/"

    url = url + var_json['endpoints'][endpoint]

    return url

def get_idkey(endpoint):
    url = get_url(endpoint)
    res = requests.get(url)
    data = res.json()
    data = data['data']
    idname = var_json['id'][endpoint]
       
    return idname



def eleminator(obj):
    delkeys = list()
    for i in obj:
        if obj[i] is None or obj[i] is False :
            delkeys.append(i)
    
    for i in delkeys:
        obj.pop(i)
    
    return obj
        
def get_time():
    now = datetime.datetime.now()
    res = now.strftime("%Y%m%d%H")
    return res


def log_err(stdin):
    coloredlogs.install()
    logging.error(stdin)    

def log_warning(stdin):
    coloredlogs.install()
    logging.warning(stdin)

def assurance():
    catch = raw_input("Are you sure ? (Y/N)")
    catch = catch.upper()
    if catch == 'Y' or catch == 'YES':
        return True
    else :
        return False

def dictcleanup(obj):
    result = dict()
    keys = obj.keys()
    for key in keys:
        temp = key.encode('utf-8')
        result[temp] = obj[key].encode('utf-8')

    return result

def listcleanup(obj):
    for row in obj:
        row = row.encode('utf-8')
    return row

# def get_table_head(row):
#     keys = row.keys()
#     return keys

def check_availability(obj,length):
    for i in obj:
        try:
            if int(i) > length or int(i) < 0:
                print("index {} is invalid integer and will be ignored".format(i))
                obj.remove(i)
            elif i ==',':
                pass
            else :
                print("invalid input")
        except Exception as e:
            print(str(e))
    return obj

def table_cleanup(obj):
    keys = obj[0].keys()
    temp = list()
    for key in keys:
        if 'id' in key:
            temp.append(key)
    for row in obj:
        for key in temp:
            del row[key]
    return obj
        
def get_filter(obj):
    var = {
    "--nm-record" : "nm_record",
    "--nm-zone"   : "nm_zone",
    "--type"      : "nm_type",
    "--ttl"       : "nm_ttl"
    }
    keys = obj.keys()
    result = dict()

    for key in keys:
        if key in var.keys() and obj[key] is not None:
            result[var[key]] = obj[key]
    return result

