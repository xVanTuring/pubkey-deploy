# Pubkey-deploy

A Small python script for pubkey sync in multiple machine (by using Github gist)

## Usage
1. Clone or Download the repo
2. install the pip `requirements.txt`
3. provide Environment Variable 
    1. `GIST_ID` 
    2. `GIST_AUTH` if you want to upload local pubkey
    3. `PUB_KEY_FILE` if your pubkey is not `~/.ssh/id_ed25519.pub` nor `~/.ssh/id_rsa.pub`
3. run `python main.py`