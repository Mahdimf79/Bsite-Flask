import datetime

def checkNull(namevar):
    status = False
    if len(namevar) != 0:
        status = True
    return status

def checkmoney(namevar):
    status = False
    try:
        if float(namevar) >= 5:
            status = True
    except:
        status = False

    return status

def checktime(date):
    status = True

    dateone = datetime.datetime.now()

    datecast = date.split('-')

    checkmonth = datecast[1]

    if '0' in checkmonth:
        checkmonth = checkmonth[1]

    datetow = datetime.datetime(int(datecast[0]),int(checkmonth),int(datecast[2]),int(datecast[3]),
        int(datecast[4]))

    if dateone > datetow :
        status = False
    
    return status