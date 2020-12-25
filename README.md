Basic template for Data-Science projects with python
==============================
Templating for data products & projects, inspired by the [cookiecutter](https://drivendata.github.io/cookiecutter-data-science/) for data science project, but 'watered-down' to the most basic but functional project structure.
```
.
├── data
├── LICENSE
├── make-dirs.sh
├── notebooks
├── proj-name
│   ├── data
│   │   └── __init__.py
│   ├── __init__.py
│   ├── models
│   │   └── __init__.py
│   └── preprocessing
│       └── __init__.py
├── README.md
├── requirements.txt
└── setup.py
```

# Instructions for setting up a project after clonning the repository
## 1. Set-up a virtual environment
Using `venv` and python3
```
python3 -m venv <ENV_NAME> 
```

## 2. Install the requirements
* Activate your virtual environment and run the required installs from the `requirements.txt` file.
* Rename the `proj-name` directory to your own project name
```
pip install wheel
pip install -r requirements.txt
```
* Change the details of the `setup.py` file and locally install your package.
```
pip install -e .
```

## 3. Change the Makefile
* Change the name `<YOUR_PROJECT_NAME>` to your project name inside of the `Makefile`

# Use your own custom package inside jupyter notebooks
You have to append the ../src directory to the path of execution of the notebook.
```[python]
# OPTIONAL: Load the "autoreload" extension so that code can change
%load_ext autoreload

# OPTIONAL: always reload modules so that as you change code in src, it gets loaded
%autoreload 2

# append the /<YOUR_PROJECT_NAME>/ folder to the python path
import sys

if '../<YOUR_PROJECT_NAME>' in sys.path:
    pass
else:
    sys.path.append('../<YOUR_PROJECT_NAME>')
```
Then you can test your imports with:
```
from <YOUR_PROJECT_NAME>.data import test_imports
test_imports.say_hello()
>> hello
```

# Optional
## Add your own github repository to the project
* List the current remote repos associated with the project
```
git remote
git remote rm origin
```
* Now you can add your own github repository to the project
