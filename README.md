# Projet NHL

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

NHL data driven model


This project explores **public NHL play-by-play and player statistics data**. 

  ---------------------------- MILESTONE 1 ----------------------------

# NHL Data Exploration and Visualization

The focus is on **data wrangling**, **exploratory data analysis (EDA)**, and building **visualizations** (both simple and interactive) to better understand trends in hockey performance.

---

## Milestone 1 Overview
- Collected **aggregated player statistics** (season-level data).  
- Collected **play-by-play data** (detailed sequences of in-game events).  
- Cleaned and structured the raw data for analysis.  
- Built visualizations to highlight patterns in player and game performance.  
- Designed interactive exploration tools to debug and better understand the data.  

This project demonstrates skills in:
- **Data wrangling & cleaning** (Python, Pandas, NumPy)  
- **Data visualization** (Matplotlib, Seaborn, Plotly)  
- **Working with APIs** (retrieving structured JSON data from the NHL stats API)  
- **Reproducible workflows** (requirements file, virtual environments, modular code)  

---

### Requirements
- Python 3.9+  
- `pip` or `conda`  
- Web browser for viewing results  

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         Visualisation and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── Visualisation   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes Visualisation a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------
