
def convTime(RFC):
    #"1985-04-12T23:20:50.52Z"
    hours = int(RFC[11:13])
    minutes = int(RFC[14:16])
    seconds = int(RFC[17:19])
    return hours,minutes,seconds