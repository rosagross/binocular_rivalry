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
- Randomization of blue/red images: blocks with an even ID (couted per condition), are rivalry_redhouse, red_face and blue_house. Odd IDs are rivalry_redface, blue_face and red_house. Example: if the first block is an unambiguous block, it will have trial ID 1. This should display the face in blue and the house in red. Then the next block will be a rivarly block with the ID 1 (since it is the first rivalry block) and thus show the red face and blue house. Other options to prevent that the subjects starting with ambiguous blocks will always see the red_house and blue_face combination: make it completely random and risking that many participant see the image colors in the same order, or making it change for every fourth participant.

<br>

**TODO**

- check the size of the stimulus! Looks way to small...
- the stimulus switches are very choppy.. should I include a fade-in/out?
- include the percept duration as parameter in the Task settings, because the computation of the phase durations of the stimuli is a bit off.. sometimes the stimulus is only shown veery short