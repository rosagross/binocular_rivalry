#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/01/25 17:33:27
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

from psychopy import event
import numpy as np
from exptools2.core.trial import Trial
from psychopy.hardware import keyboard
import os
opj = os.path.join


class BRTrial(Trial):
    """ 
    This class implements the construction of the trials in the experiment. 
    Note that the rivalry block only has one trial, since the image does not change, 
    whereas the unambiguous block has several trials, since it alternates between the house and face stimulus.
    """

    def __init__(self, session, trial_nr, block_ID, block_type, trial_type, color_comb, response_hand, phase_duration, timing, *args, **kwargs):
        
        super().__init__(session, trial_nr, phase_duration,
                         parameters={'block_type': block_type,
                                     'trial_type': trial_type, 
                                     'trial_nr': trial_nr, 
                                     'color_comb': color_comb,
                                     'response_hand': response_hand},
                         timing = timing,
                         verbose=False, *args, **kwargs)
        
        # store if it is a rivalry trial or unambiguous trial 
        self.ID = trial_nr
        self.block_ID = block_ID
        self.block_type = block_type
        self.trial_type = trial_type # this can be either house_face, house or face
        self.color_comb = color_comb # either redface or redhouse, used to draw correct image
        
            
    def draw(self):
        ''' This tells what happens in the trial, and this is defined in the session itself. '''
        self.session.draw_stimulus(self.phase)


    def get_events(self):
        """ Logs responses/triggers """

        keys = self.session.kb.getKeys(waitRelease=True)
        for thisKey in keys:
            if thisKey=='q':  # it is equivalent to the string 'q'
                print("End experiment!")
                self.session.save_output()

                if self.session.settings['Task settings']['Screenshot']==True:
                    print('\nSCREENSHOT\n')
                    self.session.win.saveMovieFrames(opj(self.session.screen_dir, self.session.output_str+'_Screenshot.png'))
                self.session.close()
                self.session.quit()
            else: 
                print(thisKey.name, thisKey.tDown, thisKey.rt)
                t = thisKey.rt
                idx = self.session.global_log.shape[0]     
                if self.block_type == 'unambiguous':
                    self.session.unambiguous_responses += 1
                    self.session.total_responses += 1
                    # check if the button was pressed correctly for the shift
                    response_delay = t - self.session.global_log.loc[idx-1, 'onset']
                    print("\nresponse delay:", response_delay)
                    print("previous timing:", self.session.global_log.loc[idx-1, 'onset'])
                    if (response_delay >= self.session.response_interval[0]) and (response_delay <= self.session.response_interval[1]):
                        print("delay (within reponse interval!):", response_delay)
                        self.session.correct_responses += 1 
                    else:
                        print("respone took too long or was too quick!")
                
                if self.block_type == 'rivalry':
                    self.session.rivalry_responses += 1
                    self.session.total_responses += 1

                event_type = self.trial_type
                print("sessions clock", self.session.clock.getTime())
                       
                self.session.global_log.loc[idx, 'event_type'] = event_type
                self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
                self.session.global_log.loc[idx, 'onset'] = t
                self.session.global_log.loc[idx, 'key_duration'] = thisKey.duration
                self.session.global_log.loc[idx, 'phase'] = self.phase
                self.session.global_log.loc[idx, 'response'] = thisKey.name
                self.session.global_log.loc[idx, 'response_button'] = self.session.response_button
                self.session.global_log.loc[idx, 'nr_frames'] = 0

                for param, val in self.parameters.items():
                    self.session.global_log.loc[idx, param] = val

                if self.eyetracker_on:  # send message to eyetracker
                    msg = f'start_type-{event_type}_trial-{self.trial_nr}_phase-{self.phase}_key-{thisKey.name}_time-{t}_duration-{thisKey.duration}'
                    self.session.tracker.sendMessage(msg)

                if thisKey.name == 'p':
                    input('PAUSE. Press enter to continue.')

                if thisKey.name in self.session.break_buttons:
                    print('NEXT PHASE')
                    self.exit_phase = True

        
                    


 

    



    
        
