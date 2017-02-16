def convTime(RFC):
    #"1985-04-12T23:20:50.52Z"
    year = int(RFC[0:4])
    month = int(RFC[5:7])
    day = int(RFC[8:10])
    hours = int(RFC[11:13])
    minutes = int(RFC[14:16])
    seconds = int(RFC[17:19])
    return year,month,day,hours,minutes,seconds