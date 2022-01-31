#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/01/25 17:33:27
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''


from psychopy import event
from psychopy.visual import Circle
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
        
        super().__init__(session, trial_nr, phase_duration, verbose=False, *args, **kwargs)
        
        # store if it is a rivalry trial or unambiguous trial 
        self.ID = trial_nr
        self.block_type = block_type
        self.trial_type = trial_type # this can be either house_face, house or face
        self.fixation_dot = Circle(self.session.win, radius=0.1, edges=100)
        
            
    def draw(self):
        ''' This tells what the happens in the trial, and this is defined in the session itself. '''
        self.session.draw_stimulus()


    def get_events(self):
        """ Logs responses/triggers """
        events = event.getKeys(timeStamped=self.session.clock)
        if events:
            if 'q' in [ev[0] for ev in events]:  # specific key in settings?
                print("End experiment!")
                if self.session.settings['PRF stimulus settings']['Screenshot']==True:
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
                    


 

    



    
        
