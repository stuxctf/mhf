import time

def Get_Time():

    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print (current_time)
