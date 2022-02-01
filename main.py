#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/01/24 16:33:53
@author  :   rosagross
@contact :   grossmann.rc@gmail.com


This is the python file to execute from command line. 
It reads the commands and initializes the session. 
'''

import sys
import os
import re
from datetime import datetime
from session import BinocularRivalrySession
datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    subject = sys.argv[1]
    sess = sys.argv[2] # so for example if something went wrong and we wanna to the experiment again, increase session number when starting

    subject_ID = int(re.findall(r'(?<=-)\d+', subject)[0])
    output_str = subject + '_' + sess
    output_dir = './output_data/'+output_str+'_Logs'
    settings_file = './settings.yml'
    eyetracker_on = False

    if not os.path.exists('./output_data'):
        os.mkdir('./output_data')

    if os.path.exists(output_dir):
        print("Warning: output directory already exists. Renaming to avoid overwriting.")
        output_dir = output_dir + datetime.now().strftime('%Y%m%d%H%M%S')
    
    # instantiate and run the session 
    experiment_session = BinocularRivalrySession(output_str, output_dir, settings_file, subject_ID, eyetracker_on)
    experiment_session.run()


if __name__ == '__main__':
    main()

