#!/usr/bin/env python3
import requests, json, subprocess, sys
from decimal import Decimal

# ──────────────────────────────────────────────────────────────────────────────
NODE_URL         = "https://rpc.elys.network:443"
COMMIT_API       = "https://api.elys.network/elys-network/elys/commitment/show_commitments/"
CHAIN_ID         = "elys-1"
FEE_DENOM        = "uelys"
FEE_AMOUNT       = "477"
GAS_LIMIT        = "190509"
# 90 days @ 3s per block
NUM_BLOCKS       = 2_046_316
TX_FILENAME      = "claim-vesting.json"
SIGNED_FILENAME  = "signed-claim-vesting.json"
# ──────────────────────────────────────────────────────────────────────────────

def fetch_json(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def run_noninteractive(cmd):
    """Run a command, capture stdout for processing."""
    try:
        out = subprocess.run(cmd, shell=True, check=True,
                             capture_output=True, text=True)
        return out.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running `{cmd}`:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_current_height():
    resp = fetch_json(f"{NODE_URL}/status")
    si = resp.get("result", {}).get("sync_info")
    if not si or "latest_block_height" not in si:
        print("Unexpected /status response", file=sys.stderr)
        sys.exit(1)
    return int(si["latest_block_height"])

def get_commitments(addr):
    return fetch_json(COMMIT_API + addr)

def extract_claimable(data, height):
    total = Decimal(0)
    for tok in data["commitments"]["vesting_tokens"]:
        if tok["denom"] != FEE_DENOM:
            continue

        total_amt   = Decimal(tok["total_amount"])
        claimed_amt = Decimal(tok["claimed_amount"])
        start_blk   = int(tok["start_block"])
        elapsed     = max(0, height - start_blk)
        vested_blks = min(NUM_BLOCKS, elapsed)
        vested      = (total_amt * vested_blks) // NUM_BLOCKS
        can         = vested - claimed_amt
        if can > 0:
            total += can

    return int(total)

def make_tx(addr):
    return {
      "body": {
        "messages": [
          {"@type": "/elys.commitment.MsgClaimVesting", "sender": addr}
        ],
        "memo": ""
      },
      "auth_info": {
        "signer_infos": [],
        "fee": {
          "amount": [{"denom": FEE_DENOM, "amount": FEE_AMOUNT}],
          "gas_limit": GAS_LIMIT
        }
      },
      "signatures": []
    }

def main():
    print("Elys Vesting Claim Tool")
    address = input("Enter your Elys wallet address: ").strip()

    print("Fetching current block height…")
    height = get_current_height()
    print(f"Latest height: {height}")

    print(f"Fetching vesting data for {address}…")
    data = get_commitments(address)

    claim_uelys = extract_claimable(data, height)
    if claim_uelys == 0:
        print("No vested EDEN available to redeem as ELYS right now.")
        return

    human = Decimal(claim_uelys) / Decimal(1_000_000)
    print(f"Redeemable EDEN as ELYS: {human:.6f} ELYS ({claim_uelys:,} uelys)")

    with open(TX_FILENAME, "w") as f:
        json.dump(make_tx(address), f, indent=2)
    print(f"Transaction JSON written to {TX_FILENAME}")

    choice = input("Do you want to sign and broadcast now? [y/N]: ").strip().lower()
    if choice != "y":
        print("To sign later:")
        print(f"  elysd tx sign {TX_FILENAME} --from <KEY> --chain-id {CHAIN_ID} "
              f"--output-document {SIGNED_FILENAME}")
        print(f"  elysd tx broadcast {SIGNED_FILENAME} --node {NODE_URL}")
        return

    key_name = input("Enter your signing key name: ").strip()

    # sign (interactive)
    print("Signing transaction…")
    subprocess.run(
        f"elysd tx sign {TX_FILENAME} --from {key_name} "
        f"--chain-id {CHAIN_ID} --node {NODE_URL} "
        f"--output-document {SIGNED_FILENAME}",
        shell=True,
        check=True
    )

    # broadcast (interactive)
    print("Broadcasting transaction…")
    subprocess.run(
        f"elysd tx broadcast {SIGNED_FILENAME} --node {NODE_URL}",
        shell=True,
        check=True
    )

if __name__ == "__main__":
    main()
