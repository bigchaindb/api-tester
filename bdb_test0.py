
import time
import json
import argparse
import requests
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair


def print_http_response(r):
    print('response.elapsed (time) = {}'.format(r.elapsed))
    print('response.status_code = {}'.format(r.status_code))
    print('response.reason = {}'.format(r.reason))
    print('response.headers = {}'.format(r.headers))
    parsed_text = json.loads(r.text)
    print('pretty(response.text):')
    print(json.dumps(parsed_text, indent=4))


# Parse all the command-line arguments
parser = argparse.ArgumentParser(
    description="Test a BigchainDB node's HTTP API."
    )
parser.add_argument('subdomain', type=str,
                    help='subdomain in https://subdomain/api/v1/')
parser.add_argument('service_key', type=str, help='PagerDuty service key')
args = parser.parse_args()

# Create an object of class BigchainDB
root_url = 'https://' + args.subdomain
bdb = BigchainDB(root_url)

print('Testing the HTTP API at ' + root_url)
print('Note: This script only tests the POST /transactions endpoint')

# Create two users
user1 = generate_keypair()
user2 = generate_keypair()

# Generate a digital asset
asset = {'data': {'type': 'test asset', 'time': time.strftime('%X %x %Z')}}
print('Generated asset = {}'.format(asset))

# POST a CREATE transaction with that asset in it
prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=user1.public_key,
    asset=asset,
)

fulfilled_creation_tx = bdb.transactions.fulfill(
    prepared_creation_tx,
    private_keys=user1.private_key,
)

# A handy snippet to make the transaction invalid (for testing purposes)
# fulfilled_creation_tx['id'] = 'abc123'

#  sent_creation_tx = bdb.transactions.send(fulfilled_creation_tx)
headers = {}
headers.update({'Content-Type': 'application/json'})
api_root_endpoint = root_url + '/api/v1'
tx_endpoint = api_root_endpoint + '/transactions/'

print('Posting request...')

r = requests.post(
    tx_endpoint,
    # verify=False,  #'/usr/local/share/ca-certificates/',
    headers=headers,
    json=fulfilled_creation_tx,
)
print_http_response(r)

# If the response.status_code wasn't 202 (ACCEPTED)
# then trigger a new incident on PagerDuty
if int(r.status_code) != 202:
    pagerduty_endpoint = \
        'https://events.pagerduty.com/generic/2010-04-15/create_event.json'
    evt_body = {}
    evt_body['service_key'] = args.service_key
    evt_body['event_type'] = 'trigger'
    desc = 'After POSTing a transaction to {} '.format(root_url)
    desc += 'the HTTP response status code was not 202, '
    desc += 'it was {}'.format(r.status_code)
    evt_body['description'] = desc
    evt_body['client'] = 'testbot'

    r2 = requests.post(
         pagerduty_endpoint,
         json=evt_body,
    )

    print('The HTTP response status code was not 202, '
          'so a trigger event was '
          'generated and sent to PagerDuty. '
          'This was the response from PagerDuty:')
    print_http_response(r2)