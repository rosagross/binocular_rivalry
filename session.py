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
from psychopy.hardware import keyboard
from exptools2.core import PylinkEyetrackerSession
from trial import BRTrial
import random

opj = os.path.join


class BinocularRivalrySession(PylinkEyetrackerSession):

    def __init__(self, output_str, output_dir, settings_file, subject_ID, eyetracker_on):
        """ Initializes BinocularRival object. 
      
        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs)
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        subject_ID : int
            ID of the current participant
        eyetracker_on : bool 
            Determines if the cablibration process is getting started.
        """
            
        super().__init__(output_str, output_dir, settings_file, eyetracker_on=eyetracker_on)  # initialize using parent class constructor!
        self.subject_ID = subject_ID
        self.n_blocks = self.settings['Task settings']['Blocks'] #  for now this can be set in the setting file! 
        self.stim_duration_rivalry = self.settings['Task settings']['Stimulus duration rivalry']
        self.path_to_stim = self.settings['Task settings']['Stimulus path']
        self.stim_size = self.settings['Task settings']['Stimulus size']
        self.previous_percept_duration = self.settings['Task settings']['Previous percept duration']
        self.percept_jitter = self.settings['Task settings']['Percept duration jitter']
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
        self.nr_unambiguous_trials = 0

        # randomly choose if the participant responds with the right or the left hand
        self.response_hand = 'preferred' # 'left' if random.uniform(1,100) < 50 else 'right'

        # randomly choose if the participant responds with the right BUTTON to house or face
        self.response_button = 'upper_house' if random.uniform(1,100) < 50 else 'upper_face'

        # initialize the keyboard for the button presses
        self.kb = keyboard.Keyboard()


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

        # build an array with the possible color combinations 
        # (has to be done BEFORE we construct the trials below)
        color_combinations = ['redface', 'redhouse']
        colors_list = []
        # add the colorcombination alternatingly 
        for i in range(int(self.n_blocks/2)):
            # if there is an odd nr. of trials we should choose the last block randomly!
            if ((self.n_blocks%2) != 0) and (i == self.n_blocks-1):
                idx = 0 if random.uniform(1,100) < 50 else 1
            else:
                idx = 0 if (i%2)==0 else 1 
                
            colors_list.append(color_combinations[idx])

        colors_rivalry = np.array(colors_list)
        colors_ambiguous = np.array(colors_list)
        
        for i in range(self.n_blocks):
            # we start counting with 1 because the blocks with ID 0 are breaks!
            block_ID = i + 1 
            print("\ncurrent block is", block_ID)
            print("start condition", self.start_condition)

            # before every block we have an interstimulus interval where only the fixation is seen
            self.trial_list.append(BRTrial(self, 0, 0, 'break', 'break', 'break', self.response_hand,[self.phase_duration_break]))

            # equal subjects start with rivarly, unequal with unambiguous
            if (block_ID + self.start_condition) % 2 == 0:
                block_ID_rivalry += 1
                block_type = 'rivalry'
                # determine type and color combination
                np.random.shuffle(colors_rivalry)
                trial_type = 'house_face'
                color_comb = 'rivalry_' + colors_rivalry[0] 
                colors_rivalry = colors_rivalry[1:]

                self.trial_list.append(BRTrial(self, trial_nr, block_ID_rivalry, block_type, trial_type, color_comb, self.response_hand,[self.stim_duration_rivalry]))
                print("appended trial nr", trial_nr)
                trial_nr += 1 

            else:
                block_type = 'unambiguous'
                block_ID_unambig += 1
                # create the phase duration array (every image should be displayed for a different amount of time
                # but it should add up to the same duration for every unambiguous block)
                phase_durations_unambiguous = self.create_duration_array()
                print("durations unambiguous:", phase_durations_unambiguous)

                np.random.shuffle(colors_ambiguous)
                color_comb = colors_ambiguous[0] 
                colors_ambiguous = colors_ambiguous[1:]
                for i, phase_duration in enumerate(phase_durations_unambiguous):
                    # determine if next trial shows house or face
                    trial_type = 'house' if trial_nr % 2 == 0 else 'face'

                    print("appended trial nr", trial_nr)
                    print("trial number in unabiguous:", i)
                    print("phase duration", phase_duration)
                    self.trial_list.append(BRTrial(self, trial_nr, block_ID_unambig, block_type, trial_type, color_comb, self.response_hand,[phase_duration]))
                    trial_nr += 1 

        # have one break in the very end
        self.trial_list.append(BRTrial(self, 0, 0, 'break', 'break', 'break', self.response_hand,[self.phase_duration_break]))


    def create_stimulus(self):
        """ 
        This function creates house, face and rivalry stmiulus, as well as the fixation background. 
        The color of the stimulus can either be red or blue. This alternates among blocks.
        """
        self.house_red = ImageStim(self.win, image=self.path_to_stim+'house_red.bmp', units='deg', size=self.stim_size)
        self.house_blue = ImageStim(self.win, image=self.path_to_stim+'house_blue.bmp', units='deg', size=self.stim_size)
        self.face_red = ImageStim(self.win, image=self.path_to_stim+'face_red.bmp', units='deg', size=self.stim_size)
        self.face_blue = ImageStim(self.win, image=self.path_to_stim+'face_blue.bmp', units='deg', size=self.stim_size)
        self.rivalry_redface = ImageStim(self.win, image=self.path_to_stim+'rivalry_redface.bmp', units='deg', size=self.stim_size)
        self.rivalry_redhouse = ImageStim(self.win, image=self.path_to_stim+'rivalry_redhouse.bmp', units='deg', size=self.stim_size)
        self.fixation_screen = ImageStim(self.win, image=self.path_to_stim+'fixation_screen.bmp', units='deg', size=self.stim_size)
        self.test_colours = ImageStim(self.win, image=self.path_to_stim+'test.bmp', units='pix', size=768)
        self.test_house_red = ImageStim(self.win, image=self.path_to_stim+'house_red.bmp', units='deg', size=self.stim_size/2, pos=[-2,-2])
        self.test_house_blue = ImageStim(self.win, image=self.path_to_stim+'house_blue.bmp', units='deg', size=self.stim_size/2, pos=[2,-2])
        self.test_face_red = ImageStim(self.win, image=self.path_to_stim+'face_red.bmp', units='deg', size=self.stim_size/2, pos=[-2,2])
        self.test_face_blue = ImageStim(self.win, image=self.path_to_stim+'face_blue.bmp', units='deg', size=self.stim_size/2, pos=[2,2])

    def draw_stimulus(self):
        """ This function will be executed from the Trial instance, when the tiral runs. """
        
        # TODO:
        # compute the opacity to let the image fade-in/out

        # I know this is ugly, but I don't know how to make it more beautiful atm..
        if self.current_trial.trial_type == 'house_face':
            if self.current_trial.color_comb == 'rivalry_redhouse':
                self.rivalry_redhouse.draw()
            else:
                self.rivalry_redface.draw()
        elif self.current_trial.trial_type == 'face':
            if self.current_trial.color_comb == 'redface':
                self.face_red.draw()
            else: 
                self.face_blue.draw()
        elif self.current_trial.trial_type == 'house':
            if self.current_trial.color_comb == 'redface':
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
        
        
        #self.test_colours.draw()
        self.test_house_red.draw()
        self.test_house_blue.draw()
        self.test_face_blue.draw()
        self.test_face_red.draw()
        self.display_text(' ', keys='space')
        # give some instructions for the participant
        self.display_text('Please fixate the middle of the screen for the entire time\n'
                            'of the experiment.' , keys='space')
        self.display_text(f'Please use your preferred hand\n to respond.' , keys='space')
        
        if self.response_button == 'upper_house':
            button_instructions = 'Press the upper button when you see the house appear.\n Press the lower button when you see the face appear.'
        else:
            button_instructions = 'Press the upper button when you see the face appear.\n Press the lower button when you see the house appear.'
        
        self.display_text(button_instructions, keys='space')
        self.display_text('Are you ready to start the experiment?', keys='t')
        # this method actually starts the timer which keeps track of trial onsets
        self.start_experiment()
        self.kb.clock.reset()
        
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
        The jitter is added to the mean percept duration from previous studies. If the jitter is
        0.1s, a random nr between -0.1 and 0.1 is added. 
        """

        # while the number is not above the trial duration, generate more trial durations
        max_duration = self.stim_duration_rivalry
        current_duration = 0 
        phase_durations = []
        while True:
            percept_duration = self.previous_percept_duration + random.uniform(-self.percept_jitter, self.percept_jitter)
            current_duration = np.array(phase_durations).sum() + percept_duration
            if current_duration > max_duration:
                break
            
            phase_durations.append(percept_duration)
             
        current_duration = np.array(phase_durations).sum()
        duration_difference = max_duration - current_duration
        # append whats missing to the last trial
        phase_durations.append(duration_difference)
        print("duration unambiguous block:", np.array(phase_durations).sum(), "and length:", len(phase_durations))
        self.nr_unambiguous_trials = self.nr_unambiguous_trials + len(phase_durations)
        print(phase_durations)
        return phase_durations


    def calc_percept_durations(self):
        """
        Calculates the average percept duration of in the rivalry block.
        We leave out the first and last percept duration since they are determined by 
        the trial timing.
        """
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
        expected_responds = self.nr_unambiguous_trials - (self.n_blocks/2)
        print('MEAN duration between switches:', self.switch_times_mean)
        print('STD of duration between switches:', self.switch_times_std)
        print(f"Correct responses (within {self.settings['Task settings']['Response interval']}s of physical stimulus change): {self.correct_responses}")
        print("Expected responses:", expected_responds)
        np.save(opj(self.output_dir, self.output_str+'_summary_response_data.npz'), {"Reponse hand" : self.response_hand,
                                                                                     "Response button" : self.response_button,
                                                                                     "Expected number of responses (unambiguous)": expected_responds,
        														                     "Subject responses (unambiguous)": self.unambiguous_responses,
                                                                                     "Subject responses (rivalry)" : self.rivalry_responses,
        														                     f"Correct responses (within {self.settings['Task settings']['Response interval']}s of physical stimulus change)":self.correct_responses,
                                                                                     "Average percept duration across all rivalry blocks" : self.switch_times_mean,
                                                                                     "Standard deviation percept duration across all rivalry blocks" : self.switch_times_std})
        
        np.save(opj(self.output_dir, self.output_str+'_summary_response_data.npy'), {"Reponse hand" : self.response_hand,
                                                                                     "Response button" : self.response_button,
                                                                                     "Expected number of responses (unambiguous)": expected_responds,
        														                     "Subject responses (unambiguous)": self.unambiguous_responses,
                                                                                     "Subject responses (rivalry)" : self.rivalry_responses,
        														                     f"Correct responses (within {self.settings['Task settings']['Response interval']}s of physical stimulus change)":self.correct_responses,
                                                                                     "Average percept duration across all rivalry blocks" : self.switch_times_mean,
                                                                                     "Standard deviation percept duration across all rivalry blocks" : self.switch_times_std})
        


            
            

    
