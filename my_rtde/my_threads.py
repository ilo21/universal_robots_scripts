import threading
import time

#####################################################################
# CLASS FOR A SEPARATE THREAD TO KEEP ASKING IF PROGRAM IS RUNNING  #
#####################################################################

class MyIsRunningThread (threading.Thread):
    '''
        dashboard: socket to dashbord port on the robot
        the .response property will be either "true" if the program is currently running or "false" if the program is not running
    '''
    def __init__(self, dashboard):
        threading.Thread.__init__(self)
        self.dashboard = dashboard
        self.response = ""

    def run(self):
        # print("Starting thread" )
        self.read_response()
        # print("Exiting thread")

    def read_response(self):
        while(True):
            # ask for status; "running" command generates a response: "Program running: true" or "Program running: false"
            modeText = "running" + "\n"
            try:
                self.dashboard.send(modeText.encode())
                time.sleep(0.5)
                self.response = self.dashboard.recv(1024).decode().strip().split()[-1]
                # print(self.response)
                # # close the dashboard socket if the program is not running
                # if self.response == "false":
                #     self.dashboard.close()
                #     print("Closed dashboard")
            except:
                print("\nSocket did not respond.\nEnd the listening thread")
                break


######################################################
# CLASS FOR A SEPARATE THREAD SAVING DATA TO A FILE  #
######################################################

class MySavingThread (threading.Thread):
    '''
        log_path: full path to the file where new data rows will be added. Assumes that the file has already been created
        data2dump: a list of strings, each string is a row/line that will be written to the file
    '''
    def __init__(self, log_path,data2dump):
        threading.Thread.__init__(self)
        self.data2dump = data2dump
        self.log_path = log_path

    def run(self):
        # print("Starting thread" )
        self.save_data()
        # print("Exiting thread")

    def save_data(self):
        my_file = open(self.log_path, "a")
        for row in self.data2dump:
            my_file.write(row)
        my_file.close()
