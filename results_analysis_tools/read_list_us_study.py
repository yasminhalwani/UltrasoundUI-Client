import sys
import pickle

sys.path.insert(0, '../globals')


class Measurements:
    def __init__(self):
        pass

    GAZE_DATA = 1
    TOTAL_LOGS = 2


user = 1
num_task = 1
p = "P4/"
# p = ""
# version = "original/"
version = "total/"
root = "C:/Users/Yasmin/Desktop/UltrasoundUI-Yasmin/RESULTS/Clinical/" + p + version
# measurement = Measurements.GAZE_DATA
measurement = Measurements.TOTAL_LOGS

# str1 = "DEMO"
# str1 = "PHANTOM"
str1 = "PATIENT"

# <editor-fold desc="total logs">
print str1
c = 1

if measurement == Measurements.TOTAL_LOGS:
    if version == "original/":
        file_name = root + "user_" + str(user) + "/" + str1 + "/" + str1 + "_total_logs.txt"
    else:
        file_name = root + str1 + "/" + str1 + "_total_logs.txt"

if measurement == Measurements.GAZE_DATA:
    if version == "original/":
        file_name = root + "user_" + str(user) + "/" + str1 + "/" + str1 + "_" + str(num_task) + \
                    "_pog_log.txt"
    else:
        file_name = root + str1 + "/" + str1 + "_" + str(num_task) + \
                    "_pog_log.txt"

try:
    with open(file_name, 'rb') as f:
        my_list = pickle.load(f)
except:
    print "cannot open file " + file_name

print file_name
try:
    for i in range(0, len(my_list)):
        try:
            print my_list[i]['time elapsed'], c
            print c, my_list[i]
            c += 1
            if str1 == "PHANTOM":
                if c == 11:
                    print "================================" + str(c)
                if c == 7 or c == 17:
                    print "+++++++"
        except:
            print "No logs. Line # " + str(i)
except:
    print "cannot open file " + file_name

print "======================"

# </editor-fold>
