# Flask OCR API

### Requirements

- Python 3.9+
- Docker & Docker Compose

### Set the virtual env

```console
$ python -m venv venv
```

## Installation

#### Install requirements

```console
$ make install
```

#### Build docker images

```console
$ make build
```

#### Start services

```console
$ make start
```

#### Create database

```console
$ make database
```

Now, you should be able to go [localhost:5000/](localhost:5000/)  to see the app running.

---

### Stop services

```console
$ make stop
```

### Postman requests

You can import the postman collection from this [link](https://www.postman.com/lunar-equinox-903112/workspace/flask/collection/4751661-1e463176-94c3-40e7-9b67-5bc5e04784ee?action=share&creator=4751661) to test the API.

Don't forget to change the `base_url` variable to your local url, by default is `localhost:5000/`.
