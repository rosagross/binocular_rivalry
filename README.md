# Binocular Rivalry
This is repository for a simple binocular rivalry experiment. It is meant to work with an eyetracking system (EyeLink). 

**Requirements**

- python 3.6
- psychopy
- exptools

**Execution**

To execute the experiment run: python main.py sub-*xxx* ses-*x*

<br>

**NOTE** 

- Trial counting starts with 1
- The breaks have trialID and blockID of '0'
- The participant uses either the right or the left hand to respond. This is chosen completely randomly, when starting the session. Note, that when aborting a session and starting a new one, the response hand might have been changed! Carefully check the instructions in the beginning.
- Randomization of blue/red images: there two cases that should be randomized:  1) rivalry is either rivalry_redhouse or rivalry_redface. 2) unambiguous blocks are either red_face and blue_house OR blue_face and red_houseblocks. For every block the color settings are randomized BUT it is made sure that the participant has had both combinations at least one time!

<br>

**TODO**

- check the size of the stimulus! Looks way to small...
- the stimulus switches are very choppy.. should I include a fade-in/out?
- include the percept duration as parameter in the Task settings, because the computation of the phase durations of the stimuli is a bit off.. sometimes the stimulus is only shown veery short