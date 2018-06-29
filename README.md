
# Installation

I am using python 3
----------------------
Run ```git clone https://github.com/Omnistac/takehome-labs-junior-aka5hkumar.git```

This downloads the library to your computer. (using git)

next ```cd takehome-labs-junior-aka5hkumar``` and ```pip install -r requirements.txt```
This should install all of the dependencies for the program.

If this fails, here are the requirements
>pandas

> math

>scipy

>matplotlib.pyplot

>sys

>argparse

All of these should be pre-installed in python3 or part of anaconda. To install them individually run `pip install` package name. Make sure you are running an admin terminal if not using virtualenv.

Next, just run `python app.py`

That should be all. The program will ask for the data it needs. Have the bond identifiers and valid range of times handy!

Note: Do not put spaces before on in input or quotes around input.


## Commands

| Commands | Hints | Function |
|:-------------:|:-------------:|:-------------:|
| upload | make sure to use the path of the CSV file | Allows for upload of new data |
| reset | both resets both trace and quote | Resets CSV files to before new data data was uploaded |
| average | Use the identifier 'AAAAAAA' not Bond A | Takes the average trace or quote over the time range specified |
| beta |  Use the identifier 'AAAAAAA' not Bond A | Takes the daily average, then slope of that linear regression over the entire time range |
| visualize |  Use the identifier 'AAAAAAA' not Bond A | Graphs the data for a specific bond over the time range specified |
| exit | or quit | Get out of the application. Infinite Looping fails in anaconda 10 or higher. |

# My process

Attempted to build a webapp first before realizing it is not well suited to this task. Given more time, the next thing I would do is implement a REST API. I then started over and built a command line application.

Wed - thinking about app

Thurs - Built webhooks

Fri - tried to build web functions

Sat-Sun - Started over and built a cli

Monday - Debugging and documentation.

Tuesday - Submit!


Initial Instructions
-----------------------------------

## Task

* Average quote bid / offer over a given time range for a particular bond
* Average trade price over a given time range for a particular bond
* Provide the ability to upload new data
* Provide the beta estimate of a linear regression of TRACE data from any two bonds. This should change if new data is uploaded.
* Given a bond and a date rate as input, provide a visualization of the TRACE and SolveQuotes data
