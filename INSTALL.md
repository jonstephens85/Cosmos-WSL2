# Cosmos Installation

NVIDIA has only tested the installation with Ubuntu 24.04, 22.04, and 20.04. **(Note - For WSL2, I only got this to work on 22.04 and 20.04)**
The original installation assumes you are running a native Linux machine. If you are planning on running this on a Windows machine, you would need to run Cosmos via an Ubuntu install via WSL2. The following instructions will walk you through how to set that up.

## Install and Configure Ubuntu va WSL2
The original installation assumes you are running a native Linux machine. If you are planning on running this on a Windows machine, you would need to run Cosmos via an Ubuntu install via WSL2. The following instructions will walk you through how to set that up.

### Step 1: Create a new WSL 2 instance
_Skip step 1 if you are already running a suppored Ubuntu instance_

1. Open the Microsoft Store and search for **Ubuntu**
2. Select and download Ubuntu 22.04.x LTS.
3. Ubuntu will automatically install on your machine.

### Step: Modify WSL Instance Memory Access
_Skip step 2 if you have 128GB or greater System RAM_

By default, WSL only grants access to half of your system's RAM. I have found that it need between 32 and 64GB of RAM to run Cosmos. Therefore, you must modify your WSL configuration to access more memory if you have less than 128GB of system memory. Follow these steps to do so:

**Check current RAM allocation**
1. Start WSL (select your Ubuntu install from the Start menu)
2. Check your current ram: `free -h`
3. Your RAM and Swap memory will display. Swap memory is hard drive storage WSL can use in case system memory runs out. **If you have less than 64GB of RAM and 8GB of Swap, continue on the the next steps.**

**Create config file for WSL**
1. Navigate to `C:\Users\<YourUsername>\`
2. If the file `.wslconfig` doesn't exist, create it using Notepad or another text editor.
3. Open `.wslconfig` in a text editor with Administrator privileges.
4. Add or modify the config file with these lines:
```bash
[wsl2]
swap=64G
memory=64GB
```
**Restart WSL**
1. Open PowerShell or Command Prompt as Administrator.
2. Restart WSL:
```bash
wsl --shutdown
wsl
```
**Verify Changes** <br>
Verify the changes by opening Ubuntu and entering `free -h`. <br>
You should see `64G` under the Memory and Swap total.


## Install CUDA Toolkit in WSL (Optional)
If you plan to use Ubuntu via WSL for future project, I recommend installing CUDA Toolkit.
[Follow these directions to install CUDA Toolkit](https://www.youtube.com/watch?v=1HzYU2_t3yc)

I recommend installing 11.8 as most projects I am encountering are built with 11.8 compatibility first.

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
```bash
wsl --shutdown
wsl
```

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

Congrat! You have installed Cosmos on your machine. Next you must download the model checkpoints before running inference.
