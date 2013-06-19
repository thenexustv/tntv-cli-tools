curl -O http://python-distribute.org/distribute_setup.py
sudo python distribute_setup.py
sudo easy_install pip

sudo pip install mutagen
sudo pip install PyYaml
sudo pip install boto

sudo cp config-aws.yaml.sample config-aws.yaml
sudo cp config-meta.yaml.sample config-meta.yaml
echo "Please populate "
echo -e "\t config-aws.yaml with proper tokens for AWS authentication"
echo -e "\t config-meta.yaml with proper paths your composer name\n\t You will need a folder containing album as well!"