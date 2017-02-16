import operator

def convTime(RFC):
    #"1985-04-12T23:20:50.52Z"
    A = RFC.split("T")
    B = operator.itemgetter(1)(A)
    C = B.split(".")
    D = operator.itemgetter(0)(C)
    E = D.split(":")
    hours = operator.itemgetter(0)(E)
    minutes = operator.itemgetter(1)(E)
    seconds = operator.itemgetter(2)(E)