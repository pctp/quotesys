#coding:utf-8

import json

def getAccountinfo(accountfile):
    try:
        f = file(accountfile)
        setting = json.load(f)
        brokerID = str(setting['brokerID'])
        userID = str(setting['userID'])
        password = str(setting['password'])
        addr_md = str(setting['mdAddress'])
        addr_td = str(setting['tdAddress'])
        return (brokerID, userID, password, addr_md, addr_td)
    except:
        print('account file error.')



