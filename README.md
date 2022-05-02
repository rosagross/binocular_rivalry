# Binocular Rivalry
This is repository for a simple binocular rivalry experiment. An eyetracking device (EyeLink) may be connected. 

**Requirements**

- python 3.6 (3.8 works as well)
- psychopy 2022.1.1
- exptools2 (installation instructions can be found on [this repository](https://github.com/VU-Cog-Sci/exptools2))
- pylink (included in psychopy standalone, but can be retreived on the [sr-research webpage](https://www.sr-support.com/thread-48.html) as well)

**Usage**


To execute the experiment run: ```python main.py sub-xxx ses-x False\True``` <br>
The boolean operator in the end indicates if we want to run it in connection with the eyetracking device.

**Settings**
- If you would like to have contrast fading, enter the duration of the fading in frames. If not, enter 0.
- percept durations int or list (these would be predefined ones)
<br>

**Important Notes** 

- Trial counting starts with 1
- The breaks have trialID and blockID of '0'
- The participant uses the preferred hand to respond. Which finger is used for which button is indicated in the instructions. Carefully check the instructions in the beginning.
- Randomization of blue/red images: there two cases that should be randomized:  1) rivalry is either rivalry_redhouse or rivalry_redface. 2) unambiguous blocks are either red_face and blue_house OR blue_face and red_houseblocks. For every block the color settings are randomized BUT it is made sure that the participant has had both combinations at least one time!
- the phases are given in frames, but one phase is not only one screen tick (to be sure that we don't loose the phase), it is refreshrate/30

<br>

**TODO**

- check the size of the stimulus! Looks way to small...
- the stimulus switches are very choppy.. should I include a fade-in/out?
- include the percept duration as parameter in the Task settings, because the computation of the phase durations of the stimuli is a bit off.. sometimes the stimulus is only shown veery short