Compatible versions of MATLAB & Python: https://www.mathworks.com/support/requirements/python-compatibility.html

### NOTE: This only works on Windows so far with MATLAB R2021b.
### NOTE 2: MATLAB & Python must both be 64 bit. They must have the "same architecture"
From here: https://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html
# Setup:
## 1. Download MATLAB. Take note of the version! e.g. R2021b.

## 2. Download Python 3.9.0
From here: https://www.python.org/downloads/release/python-390/
Select the "Windows x86-64 executable installer".
Be sure to add it to the PATH when installing!

## 3. Install MATLAB Engine API for Python
In the folder for the project, create a .venv with VSCode.
Select the Python 3.9.0 interpreter (mine was located at: "C:\Users\Mitchell\AppData\Local\Programs\Python\Python39\python.exe")
Then, in the Terminal, with the venv activated, run:
For MATLAB R2021b:
python -m pip install matlabengine==9.11.19
For MATLAB R2023a:
python -m pip install matlabengine==9.14.6
For MATLAB R2023b:
python -m pip install matlabengine==23.2.3

# 4. In MATLAB, run:
pyenv(Version="3.9")
From here: https://www.mathworks.com/help/matlab/matlab_external/install-supported-python-implementation.html#bujjwjn



# Usage:
In process.py:
import matlab.engine
eng = matlab.engine.start_matlab()

In the body of Process.run():
varargout = eng.myfcn(varargin, nargout = length(self.output_vrs))
