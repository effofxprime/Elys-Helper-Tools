# Elys-Helper-Tools
## claim-vested-eden-to-elys.py
### Requirements:
Ran as the same user that elysd runs off of or where the elysd is installed to.

### Usage:
```bash
python3 claim-vested-eden-to-elys.py
```
You will be prompted to put in your wallet address.  This will fetch and determine how much Eden to Elys is claimable currently.  It will prompt you if you want to sign and broadcast that now or just generate the .json file so you can do it yourself.

The amount to claim is irrelevant for claiming, and once you have this .json to use to broadcast the tx, you can just continue to use it for that purpose.

Example prompts and output:
```
Elys Vesting Claim Tool
Enter your Elys wallet address: elys1mu26eqsel6ft7zf4ce596nwcmp5umegjk6txpm
Fetching current block height…
Latest height: 3008880
Fetching vesting data for elys1mu26eqsel6ft7zf4ce596nwcmp5umegjk6txpm…
Redeemable EDEN as ELYS: 56.151484 ELYS (56,151,484 uelys)
Transaction JSON written to claim-vesting.json
Do you want to sign and broadcast now? [y/N]: y
Enter your signing key name: ourwallet
Signing transaction…
Enter keyring passphrase (attempt 1/3):
Broadcasting transaction…
code: 0
codespace: ""
data: ""
events: []
gas_used: "0"
gas_wanted: "0"
height: "0"
info: ""
logs: []
raw_log: ""
timestamp: ""
tx: null
txhash: 744EED4657B3857A3EE7BF6D274643801A0CF558389D5EB0DCCF2FBC0C7426C3
```
