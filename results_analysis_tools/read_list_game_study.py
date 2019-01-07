import sys
import pickle

sys.path.insert(0, '../globals')


class Measurements:
    def __init__(self):
        pass

    GAZE_DATA = 1
    TOTAL_LOGS = 2

study = "DZ"
# study = "FZ"
# original = True
original = False
user = 5

p = "P8/"

root = "C:/Users/Yasmin/Desktop/UltrasoundUI-Yasmin/RESULTS/" + study + "/" + p
if original:
    root += "original/"

# measurement = Measurements.GAZE_DATA
measurement = Measurements.TOTAL_LOGS

num_task = 1

str1 = "MANUAL_TRAINING"
str2 = "MANUAL_RECORDED"
str3 = "GAZE_TRAINING"
str4 = "GAZE_RECORDED"

# session_names = [str1, str2, str3, str4]
session_names = [str2, str4]

for session_name in session_names:
    if measurement == Measurements.TOTAL_LOGS:
        if original:
            file_name = root + "user_" + str(
                user) + "/" + session_name + "/" + "elapsed_times/" + session_name + "_total_logs.txt"
        else:
            file_name = root + "total/" + session_name + "/" + "elapsed_times/" + session_name + "_total_logs.txt"

    if measurement == Measurements.GAZE_DATA:
        if original:
            file_name = root + "user_" + str(user) + "/" + session_name + "/" + "pog_logs/" + session_name + "_" + str(
                num_task) + \
                        "_pog_log.txt"
        else:
            file_name = root + "total/" + session_name + "/" + "pog_logs/" + session_name + "_" + str(
                num_task) + \
                        "_pog_log.txt"

    print file_name
    print session_name
    c = 1

    try:
        with open(file_name, 'rb') as f:
            my_list = pickle.load(f)
    except:
        print "cannot open file " + file_name

    try:
        for i in range(0, len(my_list)):
            try:
                if my_list[i]['user study state'] == session_name:
                    if not my_list[i]['timeout']:
                        # print my_list[i]['roi logs']
                        print my_list[i]['time elapsed']
                        c += 1
            except:
                print "No logs. Line # " + str(i)
    except:
        print "cannot open file " + file_name

    print "======================"
