# 补充
## 安装 oh my zsh
```bash
apt-get install -y git zsh && \
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" && \
sed -i 's/ZSH_THEME=\"robbyrussell\"/ZSH_THEME=\"xiong-chiamiov\"/' ~/.zshrc
```

## 临时记录
```bash
kubeadm init --apiserver-advertise-address 192.168.3.151 \
--apiserver-bind-port 6443 \
--control-plane-endpoint k8s.cluster.local:6443  \
--image-repository gcr.azk8s.cn/google_containers \
--node-name master-1 \
--pod-network-cidr 192.168.0.0/16 \
--service-cidr 10.96.0.0/12 \
--service-dns-domain cluster.local
```