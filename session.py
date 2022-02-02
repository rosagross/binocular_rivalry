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
from psychopy import event
from exptools2.core import PylinkEyetrackerSession
from trial import BRTrial
import random

opj = os.path.join


class BinocularRivalrySession(PylinkEyetrackerSession):

    def __init__(self, output_str, output_dir, settings_file, subject_ID, eyetracker_on):
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
        super().__init__(output_str, output_dir, settings_file, eyetracker_on=eyetracker_on)  # initialize using parent class constructor!
        self.subject_ID = subject_ID
        self.nr_unambiguous_trials = self.settings['Task settings']['Unambiguous trials']
        self.n_blocks = self.settings['Task settings']['Blocks'] #  for now this can be set in the setting file! 
        self.stim_duration_rivalry = self.settings['Task settings']['Stimulus duration rivalry']
        self.path_to_stim = self.settings['Task settings']['Stimulus path']
        self.phase_duration_break = self.settings['Task settings']['Break duration']
        self.exit_key = self.settings['Task settings']['Exit key']
        self.response_interval = self.settings['Task settings']['Response interval']
        
        # count the subjects responses for each condition
        self.unambiguous_responses = 0 
        self.rivalry_responses = 0 
        self.total_responses = 0
        self.correct_responses = 0 
        self.switch_times_mean = 0
        self.switch_times_std = 0 

        if self.settings['Task settings']['Screenshot']==True:
            self.screen_dir=output_dir+'/'+output_str+'_Screenshots'
            if not os.path.exists(self.screen_dir):
                os.mkdir(self.screen_dir)
        
        self.create_blocks()
        self.create_stimulus()


    def create_blocks(self):
        """creates blocks with trials by determining the block order and the shifts in the unambiguous trials"""
        self.trial_list=[]

        # define which condition starts (equal subjects are 0, unequal 1)
        self.start_condition = 0 if self.subject_ID % 2 == 0 else 1

        # for every block, the trials are created beforehand
        # note that the rivalry block only has one trial, whereas the unambiguous block has several trials
        trial_nr = 1
        block_ID_rivalry = 0 
        block_ID_unambig = 0 
        for i in range(self.n_blocks):
            # we start counting with 1 because the blocks with ID 0 are breaks!
            block_ID = i + 1 
            print("\ncurrent block is", block_ID)
            print("start condition", self.start_condition)

            # before every block we have an interstimulus interval where only the fixation is seen
            self.trial_list.append(BRTrial(self, 0, 0, 'break', 'break', [self.phase_duration_break]))

            # equal subjects start with rivarly, unequal with unambiguous
            if (block_ID + self.start_condition) % 2 == 0:
                block_ID_rivalry += 1
                block_type = 'rivalry'
                trial_type = 'house_face'
                self.trial_list.append(BRTrial(self, trial_nr, block_ID_rivalry, block_type, trial_type, [self.stim_duration_rivalry]))
                print("appended trial nr", trial_nr)
                trial_nr += 1 

            else:
                block_type = 'unambiguous'
                block_ID_unambig += 1
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
                    self.trial_list.append(BRTrial(self, trial_nr, block_ID_unambig, block_type, trial_type, [phase_duration]))
                    trial_nr += 1 

        # have one break in the very end
        self.trial_list.append(BRTrial(self, 0, 0, 'break', 'break', [self.phase_duration_break]))


    def create_stimulus(self):
        """ 
        This function creates house, face and rivalry stmiulus, as well as the fixation background. 
        The color of the stimulus can either be red or blue. This alternates among blocks.
        """
        self.house_red = ImageStim(self.win, image=self.path_to_stim+'house_red.bmp')
        self.house_blue = ImageStim(self.win, image=self.path_to_stim+'house_blue.bmp')
        self.face_red = ImageStim(self.win, image=self.path_to_stim+'face_red.bmp')
        self.face_blue = ImageStim(self.win, image=self.path_to_stim+'face_blue.bmp')
        self.rivalry_redface = ImageStim(self.win, image=self.path_to_stim+'rivalry_redface.bmp')
        self.rivalry_redhouse = ImageStim(self.win, image=self.path_to_stim+'rivalry_redhouse.bmp')
        self.fixation_screen = ImageStim(self.win, image=self.path_to_stim+'fixation_screen.bmp')
        self.test_colours = ImageStim(self.win, image=self.path_to_stim+'test.bmp')


    def draw_stimulus(self):
        """ This function will be executed from the Trial instance, when the tiral runs. """
        
        # TODO:
        # compute the opacity to let the image fade-in/out

        # I know this is ugly, but I don't know how to make it more beautiful atm..
        if self.current_trial.trial_type == 'house_face':
            if (self.current_trial.block_ID % 2) == 0:
                self.rivalry_redhouse.draw()
            else:
                self.rivalry_redface.draw()
        elif self.current_trial.trial_type == 'face':
            if (self.current_trial.block_ID % 2) == 0:
                self.face_red.draw()
            else: 
                self.face_blue.draw()
        elif self.current_trial.trial_type == 'house':
            if (self.current_trial.block_ID % 2) == 0:
                self.house_blue.draw()
            else: 
                self.house_red.draw()
        elif self.current_trial.trial_type == 'break':
            self.fixation_screen.draw()


    def run(self):
        print("-------------RUN SESSION---------------")
        
        if self.eyetracker_on:
            self.calibrate_eyetracker()
            self.start_recording_eyetracker()
        
        
        self.test_colours.draw()
        self.display_text(' ', keys='space')
        # give some intructions for the participant
        self.display_text('Please fixate the middle of the screen for the entire time\n'
                            'of the experiment. Please press'
                            ' the button when the image changes from the '
                            'house to the face and vice versa.' , keys='space')
        self.display_text('Press SPACE to start experiment', keys='space')
        # this method actually starts the timer which keeps track of trial onsets
        self.start_experiment()
        
        for trial in self.trial_list:
            self.current_trial = trial 
            self.current_trial_start_time = self.clock.getTime()
            # the run function is implemented in the parent Trial class, so our Trial inherited it
            self.current_trial.run()

        self.save_output()
        self.display_text('End. \n Thank you for participating!', keys='space')
        self.close()

    def create_duration_array(self):
        """
        Function that takes the duration entries from the setting file and constructs the 
        phase duration (duration of trial and ISI) for all trials. 
        """
        total_duration = self.stim_duration_rivalry
        nr_switches = self.nr_unambiguous_trials - 1

        assert total_duration  >= nr_switches >= 1

        # compute how long one trial would take in an equal split
        equal_duration = total_duration/self.nr_unambiguous_trials

        # draw jitters for every switch
        stdv = 1
        total_time = []
        for _ in range(nr_switches):
            jitter = np.random.normal(scale=stdv)
            trial_time = equal_duration + jitter
            total_time.append(trial_time)
            
        durations_sum = np.array(total_time).sum()
        duration_difference = total_duration - durations_sum
        # append whats missing to the last trial
        total_time.append(duration_difference)
        print("length unambiguous block (with jitter)", len(total_time))
        print(total_time)
        return total_time


    def calc_percept_durations(self):
        data_rivalry = self.global_log.loc[self.global_log['block_type'] == 'rivalry']
        # compute the average duration 
        unique_rivalry_block = data_rivalry['trial_nr'].unique()
        switch_times = []

        for rivalry_block in unique_rivalry_block:
            block = data_rivalry.loc[data_rivalry['trial_nr'] == rivalry_block]

            for i in range(len(block['onset'])-1):
                # start with the second onset (which is the first button press/first switch)
                current_onset = block['onset'].iloc[i+1]
                previous_onset = block['onset'].iloc[i]
                
                # take the previous onset and compare it to the current to get the time between perception switch 
                switch_times.append(current_onset - previous_onset)
                
        # Calculate mean and stdv 
        self.switch_times_mean = np.array(switch_times).mean()
        self.switch_times_std = np.array(switch_times).std()
        

    def save_output(self):
        
        # calculate the mean duration of percepts in rivalry blocks
        self.calc_percept_durations()
        print('MEAN duration between switches:', self.switch_times_mean)
        print('STD of duration between switches:', self.switch_times_std)
        print(f"Correct responses (within {self.settings['Task settings']['Response interval']}s of physical stimulus change): {self.correct_responses}")
        print("Expected responses:", (self.nr_unambiguous_trials-1) * (self.n_blocks/2))
        np.save(opj(self.output_dir, self.output_str+'_summary_response_data.npy'), {"Expected number of responses (unambiguous)": (self.nr_unambiguous_trials-1) * (self.n_blocks/2),
        														                      "Subject responses (unambiguous)": self.unambiguous_responses,
                                                                                      "Subject responses (rivalry)" : self.rivalry_responses,
        														                      f"Correct responses (within {self.settings['Task settings']['Response interval']}s of physical stimulus change)":self.correct_responses,
                                                                                      "Average percept duration across all rivalry blocks" : self.switch_times_mean,
                                                                                      "Stadard deviation percept duration across all rivalry blocks" : self.switch_times_std})
        


            
            

    
