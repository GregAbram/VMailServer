from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import json, pdb
from uuid import uuid1
from pymongo import MongoClient
from django.template.response import TemplateResponse


def add_vmail(request):
    try:
        s = json.loads(request.body)
        uuid = uuid1().hex
        s['uuid'] = uuid
        db = MongoClient()['vmail']
        db['vmails'].insert_one(s)
        print('ADDED ', uuid)
        return JsonResponse({"status": "ok", "uuid": uuid})
    except:
        return JsonResponse({"status": "error", "uuid": "0"})

def get_vmail(request, uuid):
    print("GV 1 ", uuid)
    db = MongoClient()['vmail']
    entry = db['vmails'].find_one({'uuid': uuid})
    print('GV 2 ', entry)
    del entry['_id']
    return JsonResponse({"status": "ok", "vmail": entry})

def _get_vmail_list():
    db = MongoClient()['vmail']
    print("XXXXX")
    return [{'name': i['name'], 'uuid': i['uuid']} for i in db['vmails'].find({})]

def  get_vmail_list_html(request):
    vmails = _get_vmail_list()
    print(vmails)
    return render(request, 'vmail_selection.html', {'vmails': vmails})
  
def get_vmail_list(request):
    try:
        vmails = _get_vmail_list()
        return JsonResponse({"status": "ok", "vmails": vmails})
    except:
        return JsonResponse({"status": "error", "vmails": {}})

def insert_vmail_snapshot_after(request, vmail, snapshot):
    print("IVSA IVSA IVSA IVSA IVSA IVSA IVSA ", vmail, snapshot)
    s = json.loads(request.body)
    print("CONTENT ", s)
    uuid = uuid1().hex
    s['vmail'] = vmail
    s['uuid'] = uuid
    s['text'] = ""
    s['url'] = "none.png"
    db = MongoClient()['vmail']
    snapshots = [i for i in db['vmail_snapshots'].find({"vmail": vmail})]
    print("SNAPSHOT LIST", snapshots)
    if len(snapshots) == 0:
        sequence = 0
    else:
        sequence = -99999
        if snapshot == "0": 
            sequence = snapshots[0]['sequence'] - 1
        elif snapshot == "1":
            sequence = snapshots[-1]['sequence'] + 1
        else:
            for i in range(len(snapshots)):
                if snapshots[i]['uuid'] == snapshot:
                    print("AAAAAAAA ", i, len(snapshots))
                    if i == (len(snapshots) - 1):
                        print("BBBBBBB")
                        sequence = snapshots[i]['sequence'] + 1
                    else:
                        print('CCCCCCCC')
                        sequence = (snapshots[i]['sequence'] + snapshots[i+1]['sequence']) / 2
        if sequence == -99999:
            return JsonResponse({"status": "sequence error", "uuid": "-1"})
    s['sequence'] = sequence
    db['vmail_snapshots'].insert_one(s)
    return JsonResponse({"status": "ok", "uuid": uuid})

# Internal call that, given a vmail uuid and a snapshot uuid (or 0, or -1) get the subsequent snapshot uuid
# First create an ordered list of snapshots for the vmail then get the appropriate next
def _get_next_snapshot(vmail, snapshot):
    print("AAAAAAAAAAA", vmail, snapshot)
    db = MongoClient()['vmail']
    snapshots = sorted([i for i in db['vmail_snapshots'].find({"vmail": vmail})], key=lambda a: a['sequence'])
    print('BBBBBBBBBBB', snapshots)
    if len(snapshots) == 0:
        return "-1"
    if snapshot == "-1":
        return "-1"    
    for i in range(len(snapshots) - 1):
        print("considering ", i, snapshot)
        if snapshots[i]['uuid'] == snapshot:
            return snapshots[i+1]['uuid']
    return "-1"

# Internal call that, given a vmail uuid and a snapshot uuid (or 0, or -1) get the previous snapshot uuid
# First create an ordered list of snapshots for the vmail then get the appropriate next
def _get_prev_snapshot(vmail, snapshot):
    db = MongoClient()['vmail']
    snapshots = sorted([i for i in db['vmail_snapshots'].find({"vmail": vmail})], key=lambda a: a['sequence'])
    if len(snapshots) == 0:
        return "-1"
    if snapshot == "0":
        return "-1"    
    for i in range(1, len(snapshots)):
        if snapshots[i]['uuid'] == snapshot:
            return snapshots[i-1]['uuid']
    return "-1"

# Get the first snapshot of the vmail
def get_first_snapshot_json(request, vmail):
    print("GFSJ GFSJ GFSJ GFSJ GFSJ ", vmail)
    db = MongoClient()['vmail']
    snapshots = sorted([i for i in db['vmail_snapshots'].find({"vmail": vmail})], key=lambda a: a['sequence'])
    if len(snapshots) == 0:
        return JsonResponse({"status": "error", "snapshot": {}})
    else:
        ss = snapshots[0]
        del ss['_id']
        return JsonResponse({"status": "ok", "snapshot": ss})

# Get the last snapshot of the vmail
def get_last_snapshot_json(request, vmail):
    db = MongoClient()['vmail']
    snapshots = sorted([i for i in db['vmail_snapshots'].find({"vmail": vmail})], key=lambda a: a['sequence'])
    if len(snapshots) == 0:
        return JsonResponse({"status": "error", "snapshot": {}})
    else:
        ss = snapshots[-1]
        del ss['_id']
        return JsonResponse({"status": "ok", "snapshot": ss})

# Given vmail and snapshot uuids, return next snapshot as json
def get_next_snapshot_json(request, vmail, snapshot):
    print("GNSJ GNSJ GNSJ GNSJ GNSJ GNSJ ", vmail, snapshot)
    next_ssid = _get_next_snapshot(vmail, snapshot)
    print("last ss: ", snapshot, " next: ", next_ssid)
    if next_ssid == "-1":
        return JsonResponse({'status': 'error', 'snapshot': {}})
    db = MongoClient()['vmail']
    next_ss = db['vmail_snapshots'].find_one({"uuid": next_ssid})
    del next_ss['_id']
    print('AAAAAA', next_ss)
    return JsonResponse({'status': 'ok', 'snapshot': next_ss})

# Given vmail and snapshot uuids, return prev snapshot as json
def get_prev_snapshot_json(request, vmail, snapshot):
    prev_ssid = _get_prev_snapshot(vmail, snapshot)
    if prev_ssid == "-1":
        return JsonResponse({'status': 'error', 'snapshot': {}})
    db = MongoClient()['vmail']
    prev_ss = db['vmail_snapshots'].find_one({"uuid": prev_ssid})
    del prev_ss['_id']
    return JsonResponse({'status': 'ok', 'snapshot': prev_ss})

# Given a vmail uuid, return page containing first snapshot
def get_first_snapshot_html(request, vmail):
    print("GFSH GFSH GFSH GFSH GFSH GFSH GFSH GFSH ", vmail)
    db = MongoClient()['vmail']
    snapshots = sorted([i for i in db['vmail_snapshots'].find({"vmail": vmail})], key=lambda a: a['sequence'])
    if len(snapshots) == 0:
        t = TemplateResponse(request, 'error.html', {'message': "vmail %s has no snapshots" % vmail}) 
        return t.render()
    ss = snapshots[0]
    del ss['_id']
    t = TemplateResponse(request, "vmail.html", {'vmail': vmail, 'snapshot': ss})
    return t.render()

# Given a vmail uuid, return uuid of first snapshot as json
def get_first_vmail_snapshot_json(vmail):
    ssid = _get_next_snapshot(vmail, "0")
    if ssid == -1:
        return JsonResponse({"status": "error", "snapshot": {}})
    db = MongoClient()['vmail']
    ss = db['vmail_snapshots'].find_one({"uuid": ssid})
    del ss['_id']
    return JsonResponse({"status": "ok", "snapshot": ss})

# Given a vmail uuid, return uuid of first snapshot as json
def get_last_vmail_snapshot_json(vmail):
    ssid = _get_next_snapshot(vmail, "-1")
    if ssid == -1:
        return JsonResponse({"status": "error", "snapshot": {}})
    db = MongoClient()['vmail']
    ss = db['vmail_snapshots'].find_one({"uuid": ssid})
    del ss['_id']
    return JsonResponse({"status": "ok", "snapshot": ss})

def insert_snapshot_field(request, snapshot, field, value):
    db = MongoClient()['vmail']
    db['vmail_snapshots'].update_one({'uuid': snapshot}, {'$set': {field: value}})
    return JsonResponse({"status": "ok"})

def upload_media(request, snapshot, ext):  
    try:
        url = uuid1().hex + ext
        fname = '%s/%s' % (settings.STATIC_ROOT, url)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXX ", fname)
        with open(fname, 'wb+') as destination:
            for chunk in request.FILES['image'].chunks():
                destination.write(chunk)
        db = MongoClient()['vmail']
        db['vmail_snapshots'].update_one({"uuid": snapshot}, {"$set": {"url": url}})
    except:
        return JsonResponse({"status": "error"})
    return JsonResponse({"status": url})

def upload_text(request, snapshot):
    try:
        print("AAAAA ", snapshot)
        text = ""
        for chunk in request.FILES['text'].chunks():
            text = text + chunk.decode()
        print("BBBBB ", text)
        db = MongoClient()['vmail']
        db['vmail_snapshots'].update_one({"uuid": snapshot}, {"$set": {"text": text}})
        print(db['vmail_snapshots'].find_one({"uuid": snapshot}))
    except:
        return JsonResponse({"status": "error"})
    return JsonResponse({"status": "ok"})


