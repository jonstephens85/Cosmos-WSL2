# Cosmos Installation

NVIDIA has only tested the installation with Ubuntu 24.04, 22.04, and 20.04. **(Note - For WSL2, I only got this to work on 22.04 and 20.04)**
The original installation assumes you are running a native Linux machine. If you are planning on running this on a Windows machine, you would need to run Cosmos via an Ubuntu install via WSL2. The following instructions will walk you through how to set that up.

## Install and Configure Ubuntu va WSL2
The original installation assumes you are running a native Linux machine. If you are planning on running this on a Windows machine, you would need to run Cosmos via an Ubuntu install via WSL2. The following instructions will walk you through how to set that up.

### Create a new WSL 2 instance
_Skip step 1 if you are already running a suppored Ubuntu instance_

1. Open the Microsoft Store and search for **Ubuntu**
2. Select and download Ubuntu 22.04.x LTS.
3. Ubuntu will automatically install on your machine.

### Modify WSL2 Swap Memory
_Skip step 2 if you have 128GB or greater System RAM_

Start WSL (select your Ubuntu install from the Start menu)
```bash
sudo swapoff -a
sudo fallocate -l 64G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Verify the changes. Enter `free -h` You should see `64G` under the Swap total.

Save this modification permanently. Open the file in the text editor: `sudo nano /etc/fstab`

Add this line to the end `/swapfile none swap sw 0 0`

Save and exit (Ctrl+O, Enter, Ctrl+X)

## Install CUDA Toolkit in WSL
[Follow these directions to install CUDA Toolkit](https://www.youtube.com/watch?v=1HzYU2_t3yc)

Cosmos works with 11.x and 12.x version. You can follow the video and just use the version you have without modifying to 11.8. Skip the section about installing Pytorch. 

## Install Docker

```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
```

Log out and back in (or restart your WSL instance) for this change to take effect.

Enable and start the Docker service: `sudo service docker start`

Test the installation to ensure it worked: `docker run hello-world`


## Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

Set Up the NVIDIA Package Repository
```bash
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```
Update Package Lists: `sudo apt-get update`

```bash
sudo apt-get install -y nvidia-container-toolkit
```
Restart Docker

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
cat /etc/docker/daemon.json
docker run --rm --gpus all nvidia/cuda:12.0.1-base-ubuntu20.04 nvidia-smi
```


## Clone the repository.

```bash
git clone git@github.com:NVIDIA/Cosmos.git
cd Cosmos
```

3. Build a Docker image using `Dockerfile` and run the Docker container.

```bash
docker build -t cosmos .
docker run -d --name cosmos_container --gpus all --ipc=host -it -v $(pwd):/workspace cosmos
docker attach cosmos_container
```
