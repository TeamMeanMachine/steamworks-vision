sudo apt-get install git-core
sudo useradd git
echo "git:2471" | sudo chpasswd # 10/10 security

sudo mkdir /home/git

# not 100% sure if a home directory gets created...
sudo chown git: /home/git
sudo chmod 777 /home/git

cd ../..
sudo git clone ./steamworks-vision /home/git/steamworks-vision
sudo chmod -R 777 /home/git/steamworks-vision
cd /home/git/steamworks-vision
git config --local receive.denyCurrentBranch updateInstead


# set up service
sudo rm -f /etc/init/tmmvision.conf
echo "start on filesystem" >> tmmvision.conf
echo "exec bin/bash /home/git/steamworks-vision/start.sh" >> tmmvision.conf
sudo mv tmmvision.conf /etc/init.d/tmmvision.conf
sudo ln -s /etc/init/tmmvision.conf /etc/init.d/tmmvision

# start service
sudo service tmmvision start

echo "Done!"
