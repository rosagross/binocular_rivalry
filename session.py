#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/01/24 16:50:25
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

import numpy as np
import os
from psychopy.visual import ImageStim

from exptools2.core.session import Session
from trial import BRTrial

opj = os.path.join


class BinocularRivalrySession(Session):

    def __init__(self, output_str, output_dir, settings_file, subject_ID):
        """ Initializes StroopSession object. 
      
        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs), e.g., "sub-01_task-stroop_run-1"
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        n_trials : int
            Number of trials to present (a custom parameter for this class)
        """
        super().__init__(output_str, output_dir, settings_file)  # initialize using parent class constructor!
        self.subject_ID = subject_ID
        self.nr_unambiguous_switches = self.settings['Task settings']['Unambiguous switches']
        self.n_blocks = self.settings['Task settings']['Blocks'] #  for now this can be set in the setting file! 
        self.stim_duration_rivalry = self.settings['Task settings']['Stimulus duration rivalry']
        self.stim_duration_unambiguous = self.settings['Task settings']['Stimulus duration unambiguous']
        self.path_to_stim = self.settings['Task settings']['Stimulus path']
        
        print("stuck 1")
        if self.settings['Task settings']['Screenshot']==True:
            self.screen_dir=output_dir+'/'+output_str+'_Screenshots'
            if not os.path.exists(self.screen_dir):
                os.mkdir(self.screen_dir)
        
        print("stuck 2")

        self.create_blocks()
        self.create_stimulus()


    def create_blocks(self):
        """creates blocks with trials by determining the block order and the shifts in the unambiguous trials"""
        self.trial_list=[]

        # count the subjects responses for each condition
        self.unambiguous_responses = 0 
        self.rivalry_responses = 0 
        self.total_responses = 0 

        # define which condition starts (equal subjects are 0, unequal 1)
        self.start_condition = 0 if self.subject_ID % 2 == 0 else 1

        # for every block, the trials are created beforehand
        # note that the rivalry block only has one trial, whereas the unambiguous block has several trials
        trial_nr = 0
        for block_ID in range(self.n_blocks):
            print("current block is", block_ID)

            # equal subjects start with rivarly, unequal with unambiguous

            if block_ID +self.start_condition % 2 == 0:
                block_type = 'rivalry'
                trial_type = 'house_face'
                print("appended trial nr", trial_nr)
                self.trial_list.append(BRTrial(self, trial_nr, block_type, trial_type))
                trial_nr += 1 

            else:
                block_type = 'unambiguous'
                # TODO: for the first trial in this block we need to append a break!
                # add unambiguous trials (TODO: think about if we want to have a random\equal number of trials in every block)
                for i in range(self.nr_unambiguous_switches):
                    # determine if next trial shows house or face
                    trial_type = 'house' if trial_nr % 2 == 0 else 'face'

                    print("appended trial nr", trial_nr)
                    print("trial number in unabiguous:", i)
                    self.trial_list.append(BRTrial(self, trial_nr, block_type, trial_type))
                    trial_nr += 1 


        # times for the physical stimulus to change
        #switch_stimuli_times = 0

    def create_stimulus(self):
        """ This function creates house, face and rivalry stmiulus. """

        self.house_stim = ImageStim(self.win, image=self.path_to_stim+'replay_house.bmp')
        self.face_stim = ImageStim(self.win, image=self.path_to_stim+'replay_face.bmp')
        self.rivalry_stim = ImageStim(self.win, image=self.path_to_stim+'replay_rivalry.bmp')

    def draw_stimulus(self):
        """ This function will be executed from the Trial instance, when the tiral runs. """
        print("draw stimulus")
        if self.current_trial == 'house_face':
            self.rivalry_stim.draw()
        elif self.current_trial == 'face':
            self.face_stim.draw()
        elif self.current_trial == 'house':
            self.house_stim.draw()


    def run(self):
        print("-------------RUN SESSION---------------")
        self.display_text('Press SPACE to start experiment', keys='space')

        # this method actually starts the timer which keeps track of trial onsets
        self.start_experiment()

        for trial in self.trial_list:
            self.current_trial = trial 
            self.current_trial_start_time = self.clock.getTime()
            # the run function is implemented in the parent Trial class, so our Trial inherited it
            self.current_trial.run()

        self.close()



            
            

    
