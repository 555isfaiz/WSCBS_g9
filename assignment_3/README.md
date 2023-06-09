# Web Services and Cloudbased Systems Assignment 3

## Authors
Boyuan Xiao, Sanskar Bajpai, Yufei Wang
### Errors
To resolve some common errors, we have written the instructions for them under the [Error Resolution](#error-resolution) section.
## How to Run
Using Docker Compose:
```{shell}
docker compose up
```
To build images of each services, go to the directory and run:
```{shell}
docker build <tag/name> .
```
Available services are in [authentication](./authentication/), [url_shortener](./url_shortener/) and [id_generation](./id_generation/) respectively.

## Kubernetes Deployment

There are 2 namespaces namely -> defualt and ingress-nginx, with the following resources running in both of them 

![All k8s resources](./media/all_resources.png)

To deploy all of the aforementioned resources, go to the [k8s deployment directory](./k8s_deployment/), and run the following command for all of the yaml files in it.
`kubectl apply -f ${FileName}`

This will start all of the k8s resources.
### Ingress

We utilize [ingress-nginx](https://kubernetes.github.io/ingress-nginx/) github as our controller and the [metal load balancer](https://metallb.universe.tf/). 

To download the `ingress-nginx` controller run the following command -
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.7.1/deploy/static/provider/cloud/deploy.yaml
```

### Kubernetes secret

We use kubernetes secret to hide the JWT secret key. It is packaged in kubernetes on VM and would not be accessed from docker image, ensuring not exposed to public.

To create kubernetes secret, run the following command:
```
kubectl create secret generic <my-secret> --from-literal=secretkey=<secret_key>
```
The secrets can be checked through the command:
```
kubernetes get secrets
```

#### Note
The Load Balancer exposes an external IP, but it doesn't work on bare-metal Virtual Machine (VM). The reason is that if you are runnning on bare-metal VM, have a look at (bare metal considerations)[https://kubernetes.github.io/ingress-nginx/deploy/baremetal/#over-a-nodeport-service]
## How do I access the application

1. Access the url-shortener service through the following command http://145.100.135.160:30890/urls

2. access the url-shortener service through the following command http://145.100.135.160:30890/auth

Example usage of the application - 
![Command usage exame](./media/ingress-example.png)

### Testing

The code has been tested on the following OS-
1. MacOS (Ventura) > 13.3 
2. Linux Debian 5.10.162-1 (2023-01-21) x86_64

For Testing purposes, the VM's 160 to 162 provided for the course were used, here is the node IP for all of them
![Testing Setup](./media/Testing_Nodes.png)

## Code Reference
url_check.py: [URL checker from Django](https://github.com/django/django/blob/fdf0a367bdd72c70f91fb3aed77dabbe9dcef69f/django/core/validators.py#L69)

## Error Resolution

### Regarding Binding error for auth key
Example
![binding_error](./media/bind_error.png)

To resolve this error, simply create an `auth_key.tx` text file with random text inside, since this acts as the encryption key.