if -d /opt/pubkey-deploy; then
    echo "pubkey-deploy dected skipping clone"
else 
    git clone https://github.com/xVanTuring/pubkey-deploy /opt/pubkey-deploy
fi

cd /opt/pubkey-deploy

encryped_auth="U2FsdGVkX1/uq7o+eLF0dCNa6CbH0pmAP0QxrObcEZY3G+WMg5PSgi6BZqkJ6tbHxsGyEqwI42W6Yb0mS1nqhg=="
encryped_id="U2FsdGVkX19vGRc4JhSylIpAB/WCmHiyC0toEnT/r+l4RFMtxEi0ZJUuCpXodQSy+fWL/TQAXT4R9V+667YSTw=="


echo "Please input password: "
read password
echo "source /opt/pubkey-deploy/venv/bin/activate" > cron-job.sh
decryped_auth=$(echo $encryped_auth | openssl enc -aes128 -pbkdf2 -a -d -k $password)
decryped_id=$(echo $encryped_id | openssl enc -aes128 -pbkdf2 -a -d -k $password)
echo "export GIST_AUTH=$decryped_auth" >> cron-job.sh
echo "export GIST_ID=$decryped_id" >> cron-job.sh
echo "python3 /opt/pubkey-deploy/main.py" >> cron-job.sh


python3 -m venv venv
source venv/bin/active
pip install -r requirements.txt

bash cron-job.sh


# https://pavelespinal.com/linux/bash/how-to-encrypt-and-decrypt-text-in-bash/