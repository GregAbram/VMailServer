#! /usr/bin/env python3

from pymongo import MongoClient
m = MongoClient()['vmail']

for i in m['vmails'].find({}):
    print(i)
    for j in m['vmail_snapshots'].find({'vmail': i['uuid']}):
        print("         ", j)



