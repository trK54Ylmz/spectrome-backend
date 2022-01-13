### Spectrome backend API

![Spectrome backend](https://github.com/trK54Ylmz/spectrome-backend/workflows/Spectrome%20backend/badge.svg?branch=master)

<p align="center">
    <img src="https://github.com/trK54Ylmz/spectrome-backend/blob/master/site/images/icon.png?raw=true" width="120">
    <br>
    <img src="https://github.com/trK54Ylmz/spectrome-backend/blob/master/site/images/logo-alt.png?raw=true" width="200">
</p>

Backend API application of Spectrome.

#### Install

Install dependencies by using `pip` application,

```bash
$ pip3.7 install -r requirements.txt
```

#### Usage

Run application by using following commands, 

```bash
$ python3.7 api.py default.ini
```

Run CDN server,

```bash
$ python3.7 cdn.py default.ini
```

Run background task server,

```$
$ export CONFIG=default.ini
$ celery worker -A worker.celery
```

Run periodic task server

```bash
$ export CONFIG=default.ini
$ celery beat -A periodic --max-interval=600
```
