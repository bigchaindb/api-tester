# bdb-testnet-tests

## Overview

This repository contains a script named `bdb_test0.py`
to test a BigchainDB network's HTTP API.
It sends HTTP POST requests to the BigchainDB node at
`https://SUBDOMAIN/api/v1/`
where `SUBDOMAIN` might be `node7.zorg-network.com`, `kelly.bdbtestnet.org` or whatever.

Note: You can use [Runscope](https://www.runscope.com/) or similar to test the HTTP GET endpoints.

## Using bdb_test0.py

1. Login to PagerDuty and get your PagerDuty `SERVICE_KEY` (Service "integration key"). (If you don't have or want to use PagerDuty, you can just use a random string.)
1. [Install the BigchainDB Python Driver](https://docs.bigchaindb.com/projects/py-driver/en/latest/quickstart.html)
1. Using Python 3:
   ```text
   python3 bdb_test0.py SUBDOMAIN SERVICE_KEY
   ```

For fun, you can use [Alberto's `slack-post.py` script](https://github.com/vrde/slack-utils ) to post the output on Slack.

You could set up a cron job to run the test daily, and post the result to Slack, by creating the following bash script:

```bash
#!/bin/bash
cd ~
python3 bdb_test0.py SUBDOMAIN SERVICE_KEY > output.txt
./slack-post.py -u testbot -w SLACK_WEBHOOK -c dev -f output.txt
```

(You must replace `SUBDOMAIN`, `SERVICE_KEY` and `SLACK_WEBHOOK` with valid values.)

Make sure that `runtest.sh` and `slack-post.py` are executable:

```text
chmod +x runtest.sh
chomd +x slack-post.py
```

To create the cron job, do `crontab -e` to edit the crontab in a text editor, and add the following line:

```text
00 09 * * * /home/username/name-of-bash-script.sh
```

where `username` is your username (i.e. the output of `whoami`). The added line will run the bash script daily at 09:00.
