Initial start
1) Put your sample inputs to /input_images directory such as "input1.jpeg", "input2.jpeg" etc.
2) Run the main.py, it will handle the output saving automatically.
3) You may switch the DEBUG_MODE in main.py to True to see the real time processing of the intermediary steps.


Potential Problems
1) The light background that is similar to the card creates problems for edge detection.
2) I only tested without other objects, for example if there are other objects in the input image, how does the detection works not tested.
3) Field detection isn't perfect because the student card creates a lot of problems for dilation.
4) Text_extraction logic a little bit hardcoded, we may think something better in the future.
