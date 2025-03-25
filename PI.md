

```
sudo apt install git
sudo apt install python3-pip
```

```
sudo mkdir /opt/boondock/
sudo chown -R boondock:boondock /opt/boondock

cd /opt/boondock/
sudo git clone https://github.com/Boondock-Echo/scanner-controller.git

sudo chown -R boondock:boondock /opt/boondock/scanner-controller

cd scanner-controller

```



```
sudo chown -R boondock:boondock /opt/boondock/scanner-controller

sudo chmod +x /opt/boondock/scanner-controller/setup_bc125at.sh

sudo bash /opt/boondock/scanner-controller/setup_bc125at.sh
```