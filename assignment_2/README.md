# Web Services and Cloudbased Systems Assignment 2

## Authors
Boyuan Xiao, Sanskar Bajpai, Yufei Wang

## How to Run
Run without DB:
```{shell}
pip3 install -r requirements.txt
python3 app.py
```
Run with DB:
For this application, we used mysql. The following instructions have been tested on MacOS Ventura.
We assume that the user has brew installed. 
## users can change the mysql information in app.py (line 32)
```
brew install mysql
```
Set your config as mentioned here
## app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{username}:{password}@localhost/{database}"
```{shell}
python3 app.py --db
```
## Code Reference
url_check.py: [URL checker from Django](https://github.com/django/django/blob/fdf0a367bdd72c70f91fb3aed77dabbe9dcef69f/django/core/validators.py#L69)