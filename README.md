# 目标要求

* 通过ansible脚本, 简化安装部署一套k8s集群的工作难度

# 技能要求

* 熟悉linux的基本操作命令
* 熟悉**Ansible**的基本操作
* 熟悉Docker的基本操作
* 基本阅读完成k8s的官方文档,对k8s有一个基本的认识,了解其术语和基本概念.能够根据关键字,迅速在官网上找到对应的文档进行查阅.
* 脚本使用 **kubeadm** 来创建k8s集群, 请读者熟读[文档](https://kubernetes.io/zh/docs/reference/setup-tools/kubeadm/kubeadm/)
* 了解负载均衡的技术概念, [**HAProxy**](https://baike.baidu.com/item/haproxy/5825820?fr=aladdin) 的基本工作原理
* 了解高可用的技术概念, [**Keepalived**](https://baike.baidu.com/item/Keepalived/10346758?fr=aladdin)的基本工作原理

# 集群搭建的几大步骤

1. 准备阶段
2. 网络规划
3. 获取安装脚本
4. 根据目标主机和网络规划修改配置文件

## 准备阶段
### 目标主机

* 操作系统: **ubuntu 18.04**
* 配置主机能够使用 root 用户进行 **ssh证书登录**
* 目标主机硬件配置符合安装k8s的最低要求, [参考](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#before-you-begin)
* 若干台主机
  * 单 master 模式的集群, 需要 1 台master主机, 和至少1台的worker主机(用于跑pod负载)
  * 3 master 模式的 **负载均衡** + **高可用** 模式的集群, 需要 3 台 master 主机, 和至少1台的worker主机(用于跑pod负载)
* 所有的目标主机配置好静态IP, 同一个集群的主机, 尽量在同一个子网内

### 控制端主机

* 我们通过控制端主机进行操作, 完成整个k8s集群的创建过程
* 控制端主机上要求安装 **Python3** 环境
* 安装了 [**Ansible**](http://ansible.com.cn/), 我们通过 Ansible 进行整个集群的创建操作

### 网络要求

* 目标主机配置了静态IP

* 目标主机之间能够网络互通

* 控制端主机能够与目标主机网络互通, 控制端主机能够通过SSH证书方式,对目标主机进行ssh操作 [参考:**ssh-copy-id**](https://man.linuxde.net/ssh-copy-id)

* 目标主机能够访问公网, 以便目标主机能够下载依赖软件包和docker镜像 (离线方式的解决方案另外开篇叙述)

* k8s网络插件,采用 [Calico](https://docs.projectcalico.org/getting-started/kubernetes/quickstart)

  > 问: 为什么采用 Calico ?
  >
  > 答: 参考[这篇文章](https://zhuanlan.zhihu.com/p/53296042)的描述和评测,认为 Calico 是一个比较成熟的方案.



## 网络规划

在进行创建集群的工作之前,我们需要先集群的ip地址进行统一规划:

* 明确每一台主机的静态ip地址
* 确定每一台主机在集群里担任的角色: master, worker
* 根据主机数量(资源,成本)选择采用:
  * 单 master 集群模式
  * 多 master 集群模式 (多个 master 组成 **负载均衡** + **高可用**)
* 确定 [**控制平面**](https://kubernetes.io/zh/docs/concepts/#kubernetes-%E6%8E%A7%E5%88%B6%E9%9D%A2) 的**域名**, **IP地址**, **端口**
  * 控制平面的IP地址, 在高可用的模式下, 为高可用服务的 **虚IP**. 在单master节点的模式下, 为 master 的IP地址
  * 多 master 集群模式下, 如果控制平面使用的端口与k8s_api_server使用的端口相同(默认:6443), 则负载均衡服务不能够与master运行在同一台主机上, 否则会出现端口冲突. 在此情况下, 可以选择另外的worker主机运行负载均衡服务. 或者更改控制平面的端口为其他值,例如:7443. 但是, 这种方式下, 需要在开始创建集群之前, 先在3台master上搭建好 负载均衡+高可用 服务.
  * 通过在每台目标主机上 **/etc/hosts** 文件里添加一条 控制平面域名到IP的解析记录, 实现控制平面
* 确定k8s集群中, pod 使用的网段, 一般来说,只要和目标主机不在同一个网段即可.
* 确定k8s集群中, service 使用的网段, 不能和目标主机以及pod使用的网络在同一网段

## 获取安装脚本

* 安装脚本源代码托管在github上, [源码地址](https://github.com/LoveInShenZhen/k8s-ubuntu-ansible)

* 获取代码到控制端主机
  ```bash
  git clone https://github.com/LoveInShenZhen/k8s-ubuntu-ansible.git
  ```
## 根据目标主机和网络规划修改配置文件

### Ansible 的 hosts 文件

* hosts 文件描述了我们的 ansible 脚本要操作的目标主机

* 文件sample 如下, 文件中的配置以下文的 *[案例描述](#案例描述)* 为例:

  ```
  # 主机清单文件参考: http://ansible.com.cn/docs/intro_inventory.html
  [nodes:children]
  master
  worker
  
  [master:children]
  first_master
  other_master
  
  # host_name 只能包含 英文字母,数字,中杠线 这3种字符, 我们使用 host_name 作为k8s 的node_name, 要保证唯一性 (注: 不允许有下划线)
  # 创建集群时的第一个 Master
  [first_master]
  192.168.3.151 host_name=master-1
  
  # 需要加入到现有集群的其他 Master
  [other_master]
  192.168.3.152 host_name=master-2
  192.168.3.153 host_name=master-3
  
  [worker]
  192.168.3.154 host_name=work-1
  192.168.3.155 host_name=work-2
  
  # vip_interface 为虚IP所绑定的网卡设备名称
  [lb_and_ha]
  192.168.3.151 vip_interface=eth1
  192.168.3.152 vip_interface=eth1
  192.168.3.153 vip_interface=eth1
  
  
  [all:vars]
  ansible_ssh_user=root
  ansible_ssh_private_key_file=<请替换成你的root用户证书>
  ansible_python_interpreter=/usr/bin/python3
  ```
  
* 目标主机,按照用途和分工不同, 分成不同的组, 说明如下:

  | 组名         | 说明                                                         |
  | ------------ | ------------------------------------------------------------ |
  | nodes        | k8s集群内所有的 **master** 主机和所有的 **worker** 主机      |
  | master       | k8s集群管理节点, 包含2个 **子组**, 分别是 **first_master** 和 **other_master** |
  | first_master | 创建集群时的第一个 Master                                    |
  | other_master | 要加入到现有集群的其他 Master. 如果是 **单master** 模式下, 该组成员为空 |
  | worker       | k8s集群工作节点, 用于运行负载pod                             |
  | lb_and_ha    | 用于运行 **k8s_api_server负载均衡服务** + **高可用** 的节点  |

* 请根据网络规划, 修改分组中的主机的 **ip**, **host_name**

* **host_name** 应该是全局唯一, 只能包含 英文字母,数字,中杠线 这3种字符

  > 为什么? 
  >
  > * 在 kubeadm init 初始化集群 和 kubeadm join 添加节点到集群的时候, 都是用了 --node-name 参数来指定节点的名称, 我们的脚本是使用主机名作为此参数的值, 因此需要为每个主机单独设置一个不重复的主机名.

* 在 **lb_and_ha** 组中, 每个主机需要单独设置 **vip_interface** 参数.

  > 为什么?
  >
  > * vip_interface 被用来指定虚IP所绑定的网卡设备名称
  > * 主机上可能有不止一块网卡, 所以需要进行明确指定
  > * 主机上的多块网卡可能设置成bond模式, 通过此参数来指定虚IP绑定到指定的 bond网卡上
  
* 请设置 **ansible_ssh_private_key_file** 为root用户ssh登录目标主机的证书

### 全局配置文件

*  文件路径: roles/common/defaults/main.yml

* 文件sample 如下, 文件中的配置以下文的 *[案例描述](# 案例描述)* 为例:

  ```yaml
  ---
  # defaults file for common
  
  k8s:
      # 控制平面的 主机域名和端口号
      # ref: https://kubernetes.io/zh/docs/setup/production-environment/tools/kubeadm/high-availability/#%E4%BD%BF%E7%94%A8%E5%A0%86%E6%8E%A7%E5%88%B6%E5%B9%B3%E9%9D%A2%E5%92%8C-etcd-%E8%8A%82%E7%82%B9
      # kubeadm init --control-plane-endpoint "control_plane_dns:control_plane_port" ...(略)
      control_plane_dns: k8s.cluster.local
      control_plane_port: 7443
      # apiserver_advertise_address: 0.0.0.0
      apiserver_bind_port: 6443
      # ref: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/#pod-network
      pod_network_cidr: "192.168.0.0/16"
      service_cidr: "10.96.0.0/12"
      service_dns_domain: "cluster.local"
      image_repository: "gcr.azk8s.cn/google_containers"
  
  apt:
      docker:
          apt_key_url: https://download.docker.com/linux/ubuntu/gpg
          apt_repository: https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu
      k8s:
          apt_key_url: https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg
          apt_repository: https://mirrors.aliyun.com/kubernetes/apt/
  
  
  # master 节点个数
  master_count: "{{ groups['master'] | length }}"
  # 是否是单master模式
  single_master: "{{ (groups['master'] | length) == 1 }}"
  # 
  first_master: "{{ groups['first_master'] | first }}"
  
  ntpdate_server: cn.ntp.org.cn
  
  
  ```

* 配置参数说明

  | 参数                      | 说明                                                         |
  | ------------------------- | ------------------------------------------------------------ |
  | k8s.control_plane_dns     | 控制平面的域名                                               |
  | k8s.control_plane_port    | 控制平面的端口, 为了让 master 的主机上可以运行**k8s_api_server负载均衡服务**, 则将此端口设置成一个与**k8s.apiserver_bind_port**不同的值<br />如果是 **单master** 模式下的集群, 实际上就不需要**k8s_api_server负载均衡服务**, 可以设置的与**k8s.apiserver_bind_port** 一致 |
  | k8s.apiserver_bind_port   | k8s_api_server 服务的端口,一般不做修改,默认 6443, 请参考 kubeadm init 的 **--apiserver-bind-port** 参数 |
  | k8s.pod_network_cidr      | 请参考 kubeadm init 命令的 **--pod-network-cidr** 参数       |
  | k8s.service_cidr          | 请参考 kubeadm init 命令的 **--service-cidr** 参数           |
  | k8s.service_dns_domain    | 请参考 kubeadm init 命令的 **--service-dns-domain** 参数     |
  | k8s.image_repository      | 请参考 kubeadm init 命令的 **--image-repository** 参数<br />通过设置此参数, 安装过程就不会从默认的 k8s.gcr.io 仓库下载镜像了, 解决了 k8s.gcr.io 仓库被墙的问题.<br />我们的参数配置,使用了 [GCR Proxy Cache](http://mirror.azure.cn/help/gcr-proxy-cache.html) 镜像仓库<br />[**--image-repository** 参数使用请参考这篇文章](https://www.jianshu.com/p/d42ef0eff63f) |
  |                           |                                                              |
  | apt.docker.apt_key_url    | Docker’s official GPG key.                                   |
  | apt.docker.apt_repository | Docker’s official repository 请参考[官方文档:ununtu下安装docker-ce](https://docs.docker.com/install/linux/docker-ce/ubuntu/) |
  |                           |                                                              |
  | apt.k8s.apt_key_url       | Kubernetes 镜像源 GPG key                                    |
  | apt.k8s.apt_repository    | Kubernetes 镜像源, 参考: [阿里巴巴Kubernetes 镜像源](https://developer.aliyun.com/mirror/kubernetes?spm=a2c6h.13651102.0.0.3e221b11QiMILB) |
  |                           | 使用镜像源, 是为了解决被墙的问题                             |
  |                           |                                                              |
  | ntpdate_server            | 时间同步服务器域名                                           |



## 分阶段执行脚本

> 进入到脚本源码中的 **build_k8s** 目录 (即hosts 文件所在的目录)

### 为所有的目标主机执行初始化设置

```bash
ansible-playbook prepare_all_host.yml
```

### 将 3 个 master 组成负载均衡

> 注: 单master节点模式不需要执行此步骤
1. 检查 create_haproxy.yml 配置, 文件sample 如下, 文件中的配置以下文的 *[案例描述](# 案例描述)* 为例:

   ```yaml
   ---
   - name: Create a load blance using HAproxy
     hosts: lb_and_ha
     vars:
       # 负载均衡对外提供服务的端口
       service_bind_port: "{{ k8s.control_plane_port }}"
       # 后端服务器使用的端口, 是给下面转换的过滤器使用的, haproxy.cfg.j2 模板没有使用该变量
       backend_server_port: "{{ k8s.apiserver_bind_port }}"
       # 转换成形如: ['192.168.3.151:6443', '192.168.3.152:6443', '192.168.3.153:6443'] 的列表
       backend_servers: "{{ ansible_play_hosts_all | map('regex_replace', '^(.*)$',  '\\1:' + backend_server_port) | list }}"
       # 或者采用如下的方式, 手动设置, 这样 backend_servers 可以由集群外的主机来担任
       # backend_servers:
       #   # - "<ip>:<port>"
       #   - "192.168.3.151:6443"
       #   - "192.168.3.152:6443"
       #   - "192.168.3.153:6443"
   
       # 是否开启 haproxy stats 页面
       ha_stats_enable: True
       # haproxy stats 页面的服务端口
       ha_stats_port: 1936
       # haproxy stats 页面的 url
       ha_stats_url: /haproxy_stats
       # haproxy stats 页面的访问的用户名
       ha_stats_user: admin
       # haproxy stats 页面的访问的密码
       ha_stats_pwd: showmethemoney
       
     tasks:
       - name: check parameters
         fail:
           msg: "Please setup backend_servers parameter"
         when: backend_servers == None or (backend_servers|count) == 0 or backend_servers[0] == '' or  backend_servers[0] == '<ip>:<port>'
   
         # 进行主机的基础设置
       - import_role:
           name: basic_setup
   
       - name: install haproxy
         apt:
           update_cache: no
           pkg:
             - haproxy
           state: present
       
       - name: setup HAproxy configuration
         template:
           backup: True
           src: haproxy.cfg.j2
           dest: /etc/haproxy/haproxy.cfg
           mode: u=rw,g=r,o=r
         notify: restart HAproxy service
   
     handlers:
       - name: restart HAproxy service
         service:
           name: haproxy
           state: restarted
   ```

   

2. 在3个master上创建负载均衡服务

```bash
ansible-playbook create_haproxy.yml
```

3. 脚本运行完毕后, 我们可以在其中一台master机器上, 查看 haproxy 的监控页面, 例如: master-1 ip: 192.168.3.151
   http://192.168.3.151:1936/haproxy_stats

   ![haproxy stats](https://kklongming.github.io/res/images/haproxy_stats.jpg)

4. 

# 案例描述

* 采用多 master 集群模式
* 在 3 台 master 主机上, 部署负载均衡和高可用
* 2 台 worker

## IP地址分配

* 假设目标主机处于 192.168.3.0/24 网段,分配地址如下表所示:
  | 用于                                                         | IP地址        |
  | ------------------------------------------------------------ | ------------- |
  | --control-plane-endpoint (k8s apiServer 在本地集群的域名:端口),域名解析到右边所分配的IP地址 | 192.168.3.150 |
  | master-1                                                     | 192.168.3.151 |
  | master-2                                                     | 192.168.3.152 |
  | master-3                                                     | 192.168.3.153 |
  | worker-1                                                     | 192.168.3.154 |
  | worker-2                                                     | 192.168.3.155 |

* 控制平面网络配置规划

  | 控制平面          | 设置              | 备注                   |
  | ----------------- | ----------------- | ---------------------- |
  | 控制平面域名      | k8s.cluster.local | 可按照自己的要求自定义 |
  | IP (高可用的虚IP) | 192.168.3.150     |                        |
  | 控制平面端口      | 7443              |                        |

  

* k8s集群内部网段规划

  | 用于               | 网段          | 备注                                                         |
  | ------------------ | ------------- | ------------------------------------------------------------ |
  | --pod-network-cidr | 172.19.0.0/16 | 采用Calico网络插件时, 该设置的值要与calico.yaml中的值一致.<br /> 一致性由提供的Ansible脚本保证 |
  | --service-cidr     | 10.96.0.0/12  |                                                              |

