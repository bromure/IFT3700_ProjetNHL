
# Basic virtual environment creation
These directions are based on the documention on the [CookieCutter](https://cookiecutter-data-science.drivendata.org/using-the-template "The directions from CookieCutter") website.

```bash
# Create a virtual environment using environment.yml
make create_environment
```
```bash
# Activate the created environment
conda activate venv-name
```
```bash
# Install required packages
make requirements
```
---
# `Jupyter` Setup

Make sure to have `Jupyter` installed on your machine, then use this code to create a kernel based on your `venv` (virtual environment)
```bash
python -m ipykernel install --user --name=venv-name
```
Then, you can choose this as a kernel for the notebook in the GUI.

---

### For specific cases using `venv` and `pip`
```bash
# Create a virtual environment
python -m venv venv_name

# Activate the environment
source venv_name/bin/activate    # Mac/Linux
.\venv_name\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create the environment from the YAML file
conda env create -f environment.yml

# Activate the environment
conda activate venv_name

# Update existing environment
conda env update --file environment.yml

```

