#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/01/25 17:33:27
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''


from psychopy import event
from exptools2.core.trial import Trial
import os
opj = os.path.join


class BRTrial(Trial):
    """ 
    This class implements the construction of the trials in the experiment. 
    Note that the rivalry block only has one trial, since the image does not change, 
    whereas the unambiguous block has several trials, since it alternates between the house and face stimulus.
    """

    def __init__(self, session, trial_nr, block_type, trial_type, phase_duration, *args, **kwargs):
        
        super().__init__(session, trial_nr, phase_duration, parameters={'block_type': block_type, 'trial_type': trial_type}, verbose=False, *args, **kwargs)
        
        # store if it is a rivalry trial or unambiguous trial 
        self.ID = trial_nr
        self.block_type = block_type
        self.trial_type = trial_type # this can be either house_face, house or face
        
            
    def draw(self):
        ''' This tells what happens in the trial, and this is defined in the session itself. '''
        self.session.draw_stimulus()


    def get_events(self):
        """ Logs responses/triggers """
        events = event.getKeys(timeStamped=self.session.clock)
        if events:
            if self.session.exit_key in [ev[0] for ev in events]: 
                print("End experiment!")
                if self.session.settings['Task settings']['Screenshot']==True:
                    print('\nSCREENSHOT\n')
                    self.session.win.saveMovieFrames(opj(self.session.screen_dir, self.session.output_str+'_Screenshot.png'))
                self.session.close()
                self.session.quit()
 
            for key, t in events:
                print("\ntime:", t)
                print("key:", key)
                
                if self.block_type == 'unambiguous':
                    self.session.unambiguous_responses += 1
                    self.session.total_responses += 1
                if self.block_type == 'rivalry':
                    self.session.rivalry_responses =+ 1
                    self.session.total_responses += 1

                event_type = self.trial_type

                idx = self.session.global_log.shape[0]            
                self.session.global_log.loc[idx, 'event_type'] = event_type
                self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
                self.session.global_log.loc[idx, 'onset'] = t
                self.session.global_log.loc[idx, 'phase'] = self.phase
                self.session.global_log.loc[idx, 'response'] = key
                self.session.global_log.loc[idx, 'nr_frames'] = 0
 
                for param, val in self.parameters.items():
                    self.session.global_log.loc[idx, param] = val

        
                    


 

    



    
        
