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

## 查看 swap 信息
```bash
swapon --show --noheadings
```

## 添加其他 master 时, 需要先在 first_master 上获取 certificate key
```
┌─[root@master-1] - [~] - [Mon Mar 30, 21:00]
└─[$]> kubeadm init phase upload-certs --upload-certs
W0330 21:03:00.128099   20944 configset.go:202] WARNING: kubeadm cannot validate component configs for API groups [kubelet.config.k8s.io kubeproxy.config.k8s.io]
[upload-certs] Storing the certificates in Secret "kubeadm-certs" in the "kube-system" Namespace
[upload-certs] Using certificate key:
0c886bf3fdd3bbe787cbba706737a7fb7825c6c340edd0ae6d19d12781aebe4d
```
可以自己指定 key
```
┌─[root@master-1] - [~] - [Mon Mar 30, 21:49]
└─[$]> kubeadm init phase upload-certs --upload-certs --certificate-key=ee2fd082e6a2491a978040f5962ba8e0
W0330 21:49:47.154023   31911 configset.go:202] WARNING: kubeadm cannot validate component configs for API groups [kubelet.config.k8s.io kubeproxy.config.k8s.io]
[upload-certs] Storing the certificates in Secret "kubeadm-certs" in the "kube-system" Namespace
[upload-certs] Using certificate key:
ee2fd082e6a2491a978040f5962ba8e0
```
## master join cmd sample
```bash
kubeadm join k8s.cluster.local:6443 --token phsz1s.4a6hb09le2ymdwjj     --discovery-token-ca-cert-hash sha256:00545ed6985a015f84cd9b878e6dc21f24683501b0379cefd2909647cfe7cfe4 \
--apiserver-advertise-address 192.168.3.152 \
--apiserver-bind-port 6443 \
--control-plane \
--node-name master-2 \
--certificate-key 0c886bf3fdd3bbe787cbba706737a7fb7825c6c340edd0ae6d19d12781aebe4d
```