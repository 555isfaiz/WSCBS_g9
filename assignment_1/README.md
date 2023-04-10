# Web Services and Cloudbased Systems Assignment 1

## Authors
Boyuan Xiao, Sanskar Bajpai, Yufei Wang

## How to Run
Run without DB:
```{shell}
pip3 install -r requirements.txt
python3 app.py
```
Run with DB:
## users can change the mysql information in app.py (line 32)
## app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{username}:{password}@localhost/{database}"
```{shell}
python3 app.py --db
```
## Code Reference
url_check.py: [URL checker from Django](https://github.com/django/django/blob/fdf0a367bdd72c70f91fb3aed77dabbe9dcef69f/django/core/validators.py#L69)