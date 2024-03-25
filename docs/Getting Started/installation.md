# Installation

This page will guide you through the installation of Python, an Integrated Development Environment (IDE), and the ResearchOS package. If you want to use MATLAB with ResearchOS, you will also need to install the MATLAB Engine API for Python.

## Installing Python and an Integrated Development Environment (IDE)
1. Install Python 3.6 or later on your computer. If using MATLAB, check [this Mathworks page](https://www.mathworks.com/support/requirements/python-compatibility.html) for a list of compatible Python & MATLAB versions and the table below for the MATLAB Engine API version.
    - Windows: While I recommend [downloading Python from the official website](https://www.python.org/downloads/), on Windows machines I have found [downloading Python from the Windows store](https://apps.microsoft.com/search?query=python&hl=en-us&gl=US) to be the most user-friendly for some reason. If downloading from the official website, select the "x86 executable installer" and **be sure to add Python to your PATH** during installation.
    - Mac: You can download Python from the Python website or use [Homebrew](https://brew.sh/). If you want to use MATLAB with ResearchOS, be aware of Python version requirements for your version of MATLAB. 
2. Make sure you have a program to run Python code installed, called an Integrated Development Environment (IDE). There are many options for Python, such as [Spyder](https://www.spyder-ide.org/), [PyCharm](https://www.jetbrains.com/pycharm/), [Visual Studio Code](https://code.visualstudio.com/), or [Jupyter Notebook](https://jupyter.org/). I will be providing instructions for Visual Studio Code (VS Code), but the process is similar for other programs.

**NOTE**: For Visual Studio Code, you will need to install the Python extension. You can do this by clicking the "Extensions" icon on the left-hand side of the window, searching for "Python", and clicking "Install" on the Python extension by Microsoft.

## Installing ResearchOS
1. Create a folder on your computer where you will store your code and data. This is where you will install the ResearchOS package.
2. Set your current directory. Open a Command Prompt (Windows) or Terminal (Mac) and navigate to the folder you created in step 3. This sets that folder as the current directory. You can also do this in your IDE, which may be easier. In VS Code, you can do this by clicking "File" -> "Open Folder" and selecting the folder you created. Then, click "Terminal" -> "New Terminal" to open a terminal window in that folder.
3. Create a virtual environment in your folder. This is a way to keep your Python packages separate from the rest of your computer, and should be done for every project folder. You can do this by typing `python -m venv .venv` into the Terminal while inside the folder we created in step 1. This will create a folder called `.venv` in your current directory that contains a separate Python installation. 
4. Note that you will need to activate this environment every time you open a new terminal window. VS Code frequently activates the venv for you when opening a Terminal using "Terminal" -> "New Terminal". You can also do this by typing `source .venv/bin/activate` on Mac or `.\.venv\Scripts\Activate` on Windows. You can deactivate the environment by typing `deactivate`. *You will know that your virtual environment is activated if your terminal prompt has* `(.venv)` *at the beginning of the line.*
5. **For Windows only**: you may need to change your PowerShell settings to allow scripts to run. You can do this by opening PowerShell as an administrator and typing `Set-ExecutionPolicy RemoteSigned`. You can change this back to the default setting by typing `Set-ExecutionPolicy Restricted`. Alternatively, ensure that you are in a Command Prompt window, not PowerShell, by clicking the dropdown arrow next to the "New Terminal" button and selecting "Command Prompt". macOS and Linux users do not need to worry about this step.
6. Verify that the correct Python interpreter is being used by typing `pip -V`. This should return the path to the Python interpreter in your virtual environment. If it does not, repeat step 4.
7. Install the ResearchOS package and all of its dependencies by typing in your terminal:
```
pip install researchos
```

You can now use ResearchOS in your Python code by importing it with:
```
import researchos as ros
```

## Optional: Installing the MATLAB Engine API for Python
If you want to use MATLAB with ResearchOS, you will need to install the MATLAB Engine API for Python. This installation is separate from the MATLAB software itself. Refer to the table below for the proper Matlab Engine API version for a subset of MATLAB releases. 

To install type `pip install matlabengine==##.##.##` in the terminal. You can find more instructions for installing the MATLAB Engine API for Python [here](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html).

| MATLAB Version | MATLAB Engine API Version |
|----------------|---------------------------|
| R2023b         | 23.2.3                    |
| R2023a         | 9.14.6                    |
| R2021b         | 9.11.19                   |

If you have a MATLAB version that is not listed here and would like to contribute its corresponding MATLAB Engine API version to these docs, please open an issue or pull request on the [ResearchOS GitHub page](https://github.com/ResearchOS/ResearchOS).

## Optional: Share the MATLAB Engine for Interactivity and Faster ResearchOS Startup
By default ResearchOS starts a new MATLAB Engine process each time a [Process](../Research%20Objects/Pipeline%20Objects/process.md) runs. This is slow, and does not allow the user to interact with the MATLAB session. To speed up ResearchOS startup and allow the user to interact with the MATLAB session, you can share the MATLAB Engine process from MATLAB. To do this, in MATLAB's Command Window type `matlab.engine.shareEngine('ResearchOS')`. This will share the MATLAB interactive window's session with ResearchOS. Then, breakpoints can be set in MATLAB and the MATLAB session can be interacted with while ResearchOS is running.

To automatically share MATLAB's session with ResearchOS, add the `matlab.engine.shareEngine('ResearchOS')` to your `startup.m` file. This file is located in MATLAB's `userpath` directory, which can be found by typing `userpath` in MATLAB's Command Window. If the `startup.m` file does not exist, you can create it in the `userpath` directory. This will automatically share the MATLAB session with ResearchOS each time MATLAB is started.