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

1. Start WSL (select your Ubuntu install from the Start menu)
2. Disable Swap: `sudo swapoff -a`
3. Replace Swap file with new one: `sudo fallocate -l 64G /swapfile` This will let WSL access 64GB of your SSD when system memory runs out.
4. Add root access: `sudo chmod 600 /swapfile`
5. Initialize new Swap `sudo mkswap /swapfile`
6. Activate new Swap `sudo swapon /swapfile`
7. Verify the changes. Enter `free -h` You should see `64G` under the Swap total.
8. Open the file in the text editor: `sudo nano /etc/fstab`
9. Add this line to the end `/swapfile none swap sw 0 0`
10. Save and exit (Ctrl+O, Enter, Ctrl+X)




  



## Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).


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
