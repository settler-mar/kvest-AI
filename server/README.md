Запускать 

npm run


Открыть порты на ubuntu
https://losst.ru/kak-otkryt-port-ubuntu
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT


Запустить через доккер

docker build --tag server .
