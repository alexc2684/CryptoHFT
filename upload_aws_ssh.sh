
set -ex

SCRAPER_IP="34.227.103.159"
SCRAPER_PEM="~/saurav-mbp-09022019.pem"

scp -i ${SCRAPER_PEM} robinhood-scraper/*.secret ec2-user@${SCRAPER_IP}:~
scp -i ${SCRAPER_PEM} robinhood-scraper/*.py ec2-user@${SCRAPER_IP}:~
ssh -i ${SCRAPER_PEM} ec2-user@${SCRAPER_IP}
