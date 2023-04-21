import socket
import time
import sys
import os
from time import strftime
from datetime import datetime

import my_rtde.rtde as rtde
import my_rtde.rtde_config as rtde_config
import my_rtde.my_threads as my_threads

##################################################################################################
# PARAMETERS

# Robots IP address 
ROBOT_HOST = "130.236.222.98"
ROBOT_RTDE_PORT = 30004
DASHBOARD_PORT  = 29999
FREQUENCY = 500 # 500Hz
# the configuration xml file needs to be in the same folder as python script file
CONFIG_FILENAME = "test_record_data_point_configuration.xml"
# a folder that will be automatically created to save log files
LOG_FOLDER = "_ROBOT_LOGS"
# log files will start with the following string and timestamp will be added automatically
BEGINNING_OF_LOG_FILE = "robot_data_"
# the thread will wait for that many data points and write that many at the same time, 
# then wait for the next batch of the same size
# sort of a buffer 
SAMPLES2WRITE = 100
###################################################################################################


####################################################################################################
# SCRIPT CODE

###########################################
# DO NOT CHANGE 
# set access configuration file
conf = rtde_config.ConfigFile(CONFIG_FILENAME)
output_names, output_types = conf.get_recipe("out")

# establish the RTDE connection
con = rtde.RTDE(ROBOT_HOST, ROBOT_RTDE_PORT)
con.connect()

# get controller version
con.get_controller_version()

# setup recipes
if not con.send_output_setup(output_names, output_types, frequency=FREQUENCY):
    print("Unable to configure output")
    sys.exit()

# start data synchronization
if not con.send_start():
    print("Unable to start synchronization")
    sys.exit()
#######################################
# END DO NOT CHANGE ###################

# connect to dashboard (PolyScope commands) to mnitor status and stop the script later
dashboard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dashboard.connect((ROBOT_HOST, DASHBOARD_PORT))
time.sleep(0.5)

# start the thread where we keep asking for status if the program is running
listening_thread = my_threads.MyIsRunningThread(dashboard)
listening_thread.start()

# configure logging path 
current_path = os.path.dirname(os.path.abspath(__file__))
dump_path = os.path.join(current_path,LOG_FOLDER)
try: 
    os.mkdir(dump_path)
except:
    # print("Did not create a new folder")
    pass

# if file not created create one and write headers
log_file_name = BEGINNING_OF_LOG_FILE+datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+".txt"
log_path = os.path.join(dump_path,log_file_name)
if not os.path.exists(log_path):
    # log headers
    f = open(log_path, "a")
    f.write("Time"+","+"Force"+"\n")
    f.close()
# save collected data to a file in a separate thread
my_custom_buffer = []
# start waiting for the data
print("\nWaiting for robot data...")
while True:
    try:
        # receive the current state
        state = con.receive()
    except:
        print("Problem with receiving data...")
        break

    if state is None:
        break
    # get the information only if the program is really running
    if listening_thread.response == "true":
        ts = round(state.timestamp,3)
        val = round(state.output_double_register_0,3)
        print(ts,val)
        row_string = str(ts)+","+str(val)+"\n"
        # add that row to my virtual buffer
        my_custom_buffer.append(row_string)
        if len(my_custom_buffer) > SAMPLES2WRITE:
            # save data to a file in a separate thread
            saving_thread = my_threads.MySavingThread(log_path,my_custom_buffer)
            saving_thread.start()
            # clear buffer
            my_custom_buffer = []

# log any leftover data
saving_thread = my_threads.MySavingThread(log_path,my_custom_buffer)
saving_thread.start()
# wait to finish logging
time.sleep(1)
print("\nClosing connections...")
dashboard.close()
con.send_pause()
con.disconnect()
print("Done")
