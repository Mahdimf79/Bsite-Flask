def checkNull(namevar):
    status = False
    if len(namevar) != 0:
        status = True
    return status

def checkmoney(namevar):
    status = False
    try:
        if int(namevar) >= 5:
            status = True
    except:
        status = False

    return status
