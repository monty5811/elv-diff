# elv-diff

*get notified in Slack when something changes in Elvanto*

<img src="/example.png?raw=true">

## How it works

* Info is pulled from Elvanto (groups and people)
* The info is compared to the last time a pull was performed
* Differences are posted to Slack with the old value, new value, time of change and a link to the person/group in Elvanto
* The info is then saved for the next comparison

### Limitations

* Any changes reverted between checks will not be noticed
* Login time modifications are ignored
* `access_permissions`, `departments`, `service_types`, `demographics`, `locations` and `family` fields are ignored

## Heroku Install

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

* Click the install button
* Follow the instructions
* Setup a periodic task in the scheduler to run `./elv_diff.py`

## Local Install

```
git clone https://github.com/monty5811/elv-diff.git
cd elv-diff
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Configure

Fill in the access keys:

```
cp .env.example .env
nano .env
```

You need your Elvanto API key, domain and a Slack Incoming Webhook.
The Slack user name and channel are optional, both will default to `elvanto-updates`.
If you do not set a `MONGO_URL`, the Elvanto info will be stored in local files instead.


### Schedule

```
# open crontab:
crontab -e
# add : */15  * * * * cd <path_to_install> && venv/bin/python elv_diff.py
```
