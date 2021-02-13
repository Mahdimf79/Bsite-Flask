import re

def emailvalidate(email):
    status = False
    if re.fullmatch('(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))',email):
        status = True
    return status


def checklength(namevar,min,max):
    status = False
    if len(namevar) >= min and len(namevar) <= max :
        status = True
    return status


def checkpassword(pas,repas):
    status = False
    if pas == repas:
        status = True
    return status
