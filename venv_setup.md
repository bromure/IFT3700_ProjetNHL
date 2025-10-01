
# Using `venv` and `pip`
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

---
# `Jupyter` Setup

Make sure to have `Jupyter` installed on your machine, then use this code to create a kernel based on your `venv` (virtual environment)
```bash
# Create kernel to run .ipynb file
python -m ipykernel install --user --name=venv_name

# Access Jupyter
jupyter-lab

```