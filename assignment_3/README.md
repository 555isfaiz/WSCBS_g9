# Web Services and Cloudbased Systems Assignment 3

## Authors
Boyuan Xiao, Sanskar Bajpai, Yufei Wang

## How to Run
Run without DB:
```{shell}
pip3 install -r requirements.txt
python3 app.py --auth="http://url.to.auth.service"
python3 auth.py
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
python3 app.py --auth="http://url.to.auth.service" --db
python3 auth.py --db
```
## Run with Gateway
To try out the gateway service, run the URL shortener and authentication service first, then run the gateway.
```{shell}
python3 gateway.py
```
## Code Reference
url_check.py: [URL checker from Django](https://github.com/django/django/blob/fdf0a367bdd72c70f91fb3aed77dabbe9dcef69f/django/core/validators.py#L69)

## Kubernetes Deployment

There are 2 namespaces namely -> defualt and ingress-nginx, with the following resources running in both of them 
