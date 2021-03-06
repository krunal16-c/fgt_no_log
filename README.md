![CI Tests](https://github.com/KyleS22/friendly_ground_truth/workflows/CI%20Tests/badge.svg)  [![codecov](https://codecov.io/gh/KyleS22/friendly_ground_truth/branch/master/graph/badge.svg)](https://codecov.io/gh/KyleS22/friendly_ground_truth) ![Documentation](https://github.com/KyleS22/friendly_ground_truth/workflows/Documentation/badge.svg)
# friendly_ground_truth
A tool for manually creating ground truth masks from images where a significant amount of detail is required.  Particularily suited for large images of plant roots.

![favicon](https://github.com/KyleS22/friendly_ground_truth/blob/master/docs/images/icon.png)

# Installation
An in-depth installation guide can be found [here](https://github.com/KyleS22/friendly_ground_truth/wiki/Installation)
The latest release of the project can be downloaded [here](https://github.com/KyleS22/friendly_ground_truth/releases/latest).

## Quick Links
[Windows](#Windows)

[Ubuntu](#Ubuntu)

[MacOs](#MacOs)


## Windows
A windows executable can be downloaded [here](https://github.com/KyleS22/friendly_ground_truth/releases/latest/download/friendly_gt-windows.exe).

You should be able to just download and run it.  You may need administrator privileges.

NOTE: If windows gives a popup saying that "it protected you from a file", click on "more info", and then "run anyways".

## Ubuntu
An Ubuntu version of the app can be downloaded [here](https://github.com/KyleS22/friendly_ground_truth/releases/latest/download/friendly_gt-ubuntu.zip).

The zip file contains an executable binary file, an image, and a bash script that will install the application.  

### Copy-pasta:
#### Install
```
wget https://github.com/p2irc/friendly_ground_truth/releases/latest/download/friendly_gt-ubuntu.zip
unzip friendly_gt-ubuntu.zip
cd friendly_gt_ubuntu
bash install_friendly_gt.sh
```

At this point, if no prompt appears, the application has been installed.

Otherwise:
```
Add ~/bin to your path? (Y/N): yes
Specify bash profile file (blank uses ~/.bashrc): ~/.bash_profile # This can be left blank if you prefer
```

#### Don't Install
```
wget https://github.com/p2irc/friendly_ground_truth/releases/latest/download/friendly_gt-ubuntu.zip
unzip friendly_gt-ubuntu.zip
cd friendly_gt_ubuntu
chmod u+x friendly_gt_ubuntu-latest
./friendly_gt_ubuntu-latest
```
## MacOs
A MacOs binary can be downloaded [here](https://github.com/p2irc/friendly_ground_truth/releases/latest/download/friendly_gt_macos-latest). 

You will need to change the permissions of the binary file to be executable, and then you can run it by double clicking it in the file browser, or by navigating to it in the terminal and typing `./friendly_gt_macos-latest`.

Copy-pasta:
```
wget https://github.com/p2irc/friendly_ground_truth/releases/latest/download/friendly_gt_macos-latest
chmod u+x friendly_gt_macos-latest
./friendly_gt_macos-latest
```
An experimental MacOs application bundle can be downloaded [here](https://github.com/p2irc/friendly_ground_truth/releases/latest/download/friendly_gt_macos-app.zip).  This bundle has not been fully tested, and may not work at all.  It should be runnable just like any other mac app bundle once you have unzipped it.  If you encounter problems with this bundle, please leave a [Bug Report](https://github.com/p2irc/friendly_ground_truth/issues).

# User Manual
A user manual can be found [in the wiki](https://github.com/p2irc/friendly_ground_truth/wiki/User-Manual)

# Bug Reports
Please report any software bugs on the [issues page](https://github.com/p2irc/friendly_ground_truth/issues).

Thanks in advance for helping out!

# Development
Detailed information about development for this application can be found on the [Wiki](https://github.com/p2irc/friendly_ground_truth/wiki)

## Basic Setup
This application is developed using python3 and virtualenv.  Dependencies are found in `requirements.txt`.  To get started:

```
python -m venv env
source ./venv/bin/activate
pip install -r requirements.txt
``` 

The main entrypoint for the application is `run.py`.  To run it, simply do `python run.py -debug`.  The `-debug` flag is optional and enables logging.

## Tests
Tests have been developed using pytest, with the mocker and coverage modules.  All tests can be found in the `tests/` directory.  To run tests, make sure you are in the main repository folder:

```
pytest --cov=friendly_ground_truth ./tests --cov-branch --cov-report=term-missing

```

This will run all tests and print a coverage report specifying any missed lines.  A coverage check is run as part of all pull-requests.

Please refer to the [Wiki](https://github.com/p2irc/friendly_ground_truth/wiki) for more details about the development process.

## Documentation
Documentation can be generated with pdoc.  Make sure to `pip install pdoc3`


```
cd doc
pdoc --html ../friendly_ground_truth/
```

Internal documentation that has been generated by pdoc and can be found [here](https://kyles22.github.io/friendly_ground_truth/docs/html/friendly_ground_truth/index.html)

