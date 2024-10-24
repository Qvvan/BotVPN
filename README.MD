
Установка докера:

Для начала удалить старую версию докера:
sudo apt-get remove docker docker-engine docker.io containerd runc

Установите необходимые пакеты для работы с репозиториями HTTPS:
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common gnupg

Добавьте официальный GPG-ключ Docker:
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

Добавьте репозиторий Docker: Для Ubuntu:
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo docker --version
Или проверьте статус сервиса Docker:
sudo systemctl status docker
