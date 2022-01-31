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
from exptools2.core import PylinkEyetrackerSession
from trial import BRTrial
import random

opj = os.path.join


class BinocularRivalrySession(PylinkEyetrackerSession):

    def __init__(self, output_str, output_dir, settings_file, subject_ID, eyetracker_on=True):
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
        super().__init__(output_str, output_dir, settings_file, eyetracker_on)  # initialize using parent class constructor!
        self.subject_ID = subject_ID
        self.nr_unambiguous_trials = self.settings['Task settings']['Unambiguous trials']
        self.n_blocks = self.settings['Task settings']['Blocks'] #  for now this can be set in the setting file! 
        self.stim_duration_rivalry = self.settings['Task settings']['Stimulus duration rivalry']
        self.path_to_stim = self.settings['Task settings']['Stimulus path']
        self.phase_duration_break = self.settings['Task settings']['Break duration']

        print("stuck 1")
        if self.settings['Task settings']['Screenshot']==True:
            self.screen_dir=output_dir+'/'+output_str+'_Screenshots'
            if not os.path.exists(self.screen_dir):
                os.mkdir(self.screen_dir)
        
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
        trial_nr = 1
        for block_ID in range(self.n_blocks):
            print("\ncurrent block is", block_ID)
            print("start condition", self.start_condition)

            # before every block we have an interstimulus interval where only the fixation is seen
            self.trial_list.append(BRTrial(self, 0, 'break', 'break', [self.phase_duration_break]))

            # equal subjects start with rivarly, unequal with unambiguous
            if (block_ID + self.start_condition) % 2 == 0:
                block_type = 'rivalry'
                trial_type = 'house_face'
                self.trial_list.append(BRTrial(self, trial_nr, block_type, trial_type, [self.stim_duration_rivalry]))
                print("appended trial nr", trial_nr)
                trial_nr += 1 

            else:
                block_type = 'unambiguous'
                
                # create the phase duration array (every image should be displayed for a different amount of time
                # but it should add up to the same duration for every unambiguous block)
                phase_durations_unambiguous = self.create_duration_array()
                print("durations unambiguous:", phase_durations_unambiguous)
                for i, phase_duration in enumerate(phase_durations_unambiguous):
                    # determine if next trial shows house or face
                    trial_type = 'house' if trial_nr % 2 == 0 else 'face'

                    print("appended trial nr", trial_nr)
                    print("trial number in unabiguous:", i)
                    print("phase duration", phase_duration)
                    self.trial_list.append(BRTrial(self, trial_nr, block_type, trial_type, [phase_duration]))
                    trial_nr += 1 



    def create_stimulus(self):
        """ This function creates house, face and rivalry stmiulus. """

        self.house_stim = ImageStim(self.win, image=self.path_to_stim+'replay_house.bmp')
        self.face_stim = ImageStim(self.win, image=self.path_to_stim+'replay_face.bmp')
        self.rivalry_stim = ImageStim(self.win, image=self.path_to_stim+'rivalry.bmp')
        self.fixation_screen = ImageStim(self.win, image=self.path_to_stim+'fixation.bmp')

    def draw_stimulus(self):
        """ This function will be executed from the Trial instance, when the tiral runs. """
        if self.current_trial.trial_type == 'house_face':
            self.rivalry_stim.draw()
        elif self.current_trial.trial_type == 'face':
            self.face_stim.draw()
        elif self.current_trial.trial_type == 'house':
            self.house_stim.draw()
        elif self.current_trial.trial_type == 'break':
            self.fixation_screen.draw()


    def run(self):
        print("-------------RUN SESSION---------------")
        self.display_text('Press SPACE to start experiment', keys='space')
        self.calibrate_eyetracker()
        # this method actually starts the timer which keeps track of trial onsets
        self.start_experiment()
        self.start_recording_eyetracker()
        for trial in self.trial_list:
            self.current_trial = trial 
            self.current_trial_start_time = self.clock.getTime()
            # the run function is implemented in the parent Trial class, so our Trial inherited it
            self.current_trial.run()

        self.close()

    def create_duration_array(self):
        """
        Function that takes the duration entries from the setting file and constructs the 
        phase duration (duration of trial and ISI) for all trials. 
        The rivalry trial has a very long duration, whereas the 
        """
        total_duration = self.stim_duration_rivalry
        nr_switches = self.nr_unambiguous_trials - 1

        assert total_duration  >= nr_switches >= 1

        random_splits = random.sample(range(total_duration), nr_switches)
        random_splits.sort()

        current = 0
        total_chunks = []

        for split in random_splits:
            # calculate the difference between the current and the next
            diff = split - current
            current = split
            total_chunks.append(diff)
        diff = total_duration - current
        total_chunks.append(diff)
        return total_chunks



            
            

    
