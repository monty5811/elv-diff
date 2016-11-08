# elv-ppl-diff

*get notified in Slack when someone changes in Elvanto*

<img src="/example.png?raw=true">

## How it works

* People info is pulled from Elvanto
* The info is compared to the last time a pull was performed
* Differences are posted to Slack with the old value, new value, time of change and a link to the person in Elvanto
* The info is then saved for the next comparison

### Limitations

* Any changes reverted between checks will not be noticed
* Login time modifications are ignored
* `access_permissions`, `departments`, `service_types`, `demographics`, `locations` and `family` fields are ignored

## Install

```
git clone https://github.com/monty5811/elv-ppl-diff.git
cd elv-ppl-diff
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

### Schedule

```
# open crontab:
crontab -e
# add : */15  * * * * cd <path_to_install> && venv/bin/python elv_ppl_diff.py
```
