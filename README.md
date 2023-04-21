# universal_robots_scripts
Scripts to work with universal robot

-----------------------------
| test_record_data_point.py |
-----------------------------
is a python script that will read and log the time and one variable value that is send from running robots program.

test_record_data_point.py has to be in the same folder as test_record_data_point_configuration.xml file

-----------------------------
| record_data_pointURprogram |
------------------------------
is a folder that contains the robot program that the sript was tested on.
ur_program_sending_variable.PNG file shows marked code lines that are required for the python script to work

-----------
| my_rtde |
-----------
is a folder with the necessary rtde libraries from Universal Robots and my library with threads
