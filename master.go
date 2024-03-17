package main

import (
	"fmt"
	"os/exec"
)

func main() {
	if err := checkUbuntuVersion(); err != nil {
		fmt.Println("Error:", err)
		return
	}

	setupTerminal()

	disableSwap()

	removePackages()

	installPodman()

	installPackages()

	installContainerd()

	configureContainerd()

	startServices()

	initializeK8s()

	installCNI()

	installEtcdctl()
}

func checkUbuntuVersion() error {
	out, err := exec.Command("cat", "/etc/lsb-release").Output()
	if err != nil {
		return err
	}
	if string(out) != "20.04" {
		return fmt.Errorf("This script only works on Ubuntu 20.04!")
	}
	return nil
}

func setupTerminal() {
	cmd := `
		apt-get --allow-unauthenticated update
		apt-get --allow-unauthenticated install -y bash-completion binutils
		echo 'colorscheme ron' >> ~/.vimrc
		echo 'set tabstop=2' >> ~/.vimrc
		echo 'set shiftwidth=2' >> ~/.vimrc
		echo 'set expandtab' >> ~/.vimrc
		echo 'source <(kubectl completion bash)' >> ~/.bashrc
		echo 'alias k=kubectl' >> ~/.bashrc
		echo 'alias c=clear' >> ~/.bashrc
		echo 'complete -F __start_kubectl k' >> ~/.bashrc
		sed -i '1s/^/force_color_prompt=yes\n/' ~/.bashrc
	`
	runShellCommand(cmd)
}

func disableSwap() {
	runShellCommand("swapoff -a")
	runShellCommand("sed -i '/\\sswap\\s/ s/^\\(.*\\)$/#\\1/g' /etc/fstab")
}

func removePackages() {
	runShellCommand("kubeadm reset -f || true")
	runShellCommand("crictl rm --force $(crictl ps -a -q) || true")
	runShellCommand("apt-mark unhold kubelet kubeadm kubectl kubernetes-cni || true")
	runShellCommand("apt-get remove -y docker.io containerd kubelet kubeadm kubectl kubernetes-cni || true")
	runShellCommand("apt-get autoremove -y")
	runShellCommand("systemctl daemon-reload")
}

func installPodman() {
	cmd := `
		. /etc/os-release
		echo "deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:testing.list
		curl -L "http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${VERSION_ID}/Release.key" | sudo apt-key add -
		apt-get update -qq
		apt-get -qq -y install podman cri-tools containers-common
		rm /etc/apt/sources.list.d/devel:kubic:libcontainers:testing.list
		cat <<EOF | sudo tee /etc/containers/registries.conf
		[registries.search]
		registries = ['docker.io']
		EOF
	`
	runShellCommand(cmd)
}

func installPackages() {
	cmd := `
		apt-get install -y apt-transport-https ca-certificates
		mkdir -p /etc/apt/keyrings
		rm /etc/apt/keyrings/kubernetes-1-27-apt-keyring.gpg || true
		rm /etc/apt/keyrings/kubernetes-1-28-apt-keyring.gpg || true
		rm /etc/apt/keyrings/kubernetes-1-29-apt-keyring.gpg || true
		curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.27/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-1-27-apt-keyring.gpg
		curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-1-28-apt-keyring.gpg
		curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-1-29-apt-keyring.gpg
		echo > /etc/apt/sources.list.d/kubernetes.list
		echo "deb [signed-by=/etc/apt/keyrings/kubernetes-1-27-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.27/deb/ /" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
		echo "deb [signed-by=/etc/apt/keyrings/kubernetes-1-28-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
		echo "deb [signed-by=/etc/apt/keyrings/kubernetes-1-29-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
		apt-get --allow-unauthenticated update
		apt-get --allow-unauthenticated install -y docker.io containerd kubelet=${KUBE_VERSION}-1.1 kubeadm=${KUBE_VERSION}-1.1 kubectl=${KUBE_VERSION}-1.1 kubernetes-cni
		apt-mark hold kubelet kubeadm kubectl kubernetes-cni
	`
	runShellCommand(cmd)
}

func installContainerd() {
	runShellCommand("wget https://github.com/containerd/containerd/releases/download/v1.6.12/containerd-1.6.12-linux-amd64.tar.gz")
	runShellCommand("tar xvf containerd-1.6.12-linux-amd64.tar.gz")
	runShellCommand("systemctl stop containerd")
	runShellCommand("mv bin/* /usr/bin")
	runShellCommand("rm -rf bin containerd-1.6.12-linux-amd64.tar.gz")
	runShellCommand("systemctl unmask containerd")
	runShellCommand("systemctl start containerd")
}

func configureContainerd() {
	cmd := `
		cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
		overlay
		br_netfilter
		EOF
		sudo modprobe overlay
		sudo modprobe br_netfilter
		cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
		net.bridge.bridge-nf-call-iptables  = 1
		net.ipv4.ip_forward                 = 1
		net.bridge.bridge-nf-call-ip6tables = 1
		EOF
		sudo sysctl --system
		sudo mkdir -p /etc/containerd
	`
	runShellCommand(cmd)
}

func startServices() {
	cmd := `
		systemctl daemon-reload
		systemctl enable containerd
		systemctl restart containerd
		systemctl enable kubelet && systemctl start kubelet
	`
	runShellCommand(cmd)
}

func initializeK8s() {
	runShellCommand("rm /root/.kube/config || true")
	runShellCommand("kubeadm init --kubernetes-version=${KUBE_VERSION} --ignore-preflight-errors=NumCPU --skip-token-print --pod-network-cidr 192.168.0.0/16")
	runShellCommand("mkdir -p ~/.kube")
	runShellCommand("sudo cp -i /etc/kubernetes/admin.conf ~/.kube/config")
}

func installCNI() {
	runShellCommand("kubectl apply -f https://raw.githubusercontent.com/killer-sh/cks-course-environment/master/cluster-setup/calico.yaml")
}

func installEtcdctl() {
	cmd := `
		ETCDCTL_VERSION=v3.5.1
		ETCDCTL_ARCH=$(dpkg --print-architecture)
		ETCDCTL_VERSION_FULL=etcd-${ETCDCTL_VERSION}-linux-${ETCDCTL_ARCH}
		wget https://github.com/etcd-io/etcd/releases/download/${ETCDCTL_VERSION}/${ETCDCTL_VERSION_FULL}.tar.gz
		tar xzf ${ETCDCTL_VERSION_FULL}.tar.gz ${ETCDCTL_VERSION_FULL}/etcdctl
		mv ${ETCDCTL_VERSION_FULL}/etcdctl /usr/bin/
		rm -rf ${ETCDCTL_VERSION_FULL} ${ETCDCTL_VERSION_FULL}.tar.gz
	`
	runShellCommand(cmd)
}

func runShellCommand(cmd string) {
	out, err := exec.Command("/bin/sh", "-c", cmd).CombinedOutput()
	if err != nil {
		fmt.Printf("Error running command: %s, output: %s\n", cmd, string(out))
	}
}
