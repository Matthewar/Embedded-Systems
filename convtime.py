import operator

def convTime(RFC):
    #"1985-04-12T23:20:50.52Z"
    A = RFC.split("T")
    B = operator.itemgetter(1)(A)
    C = B.split("Z")
    D = operator.itemgetter(0)(C)
    E = D.split(".")
    F = operator.itemgetter(0)(E)
    hours = operator.itemgetter(0)(F)
    minutes = operator.itemgetter(1)(F)
    seconds = operator.itemgetter(2)(F)