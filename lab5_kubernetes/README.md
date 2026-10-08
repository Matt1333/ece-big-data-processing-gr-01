# Lab 5 - Kubernetes basics with minikube

Chapter `06.containerization-and-kubernetes`, `lab-1`. The parts 1 to 3 are done, the parts 4 to 7 are
still to do (scaling, rolling update, the yaml manifests, teardown).

## Setup

```bash
winget install Kubernetes.minikube
minikube start --driver=docker --memory=3000 --cpus=2
```

We give only 3 Go and 2 cpus because the machine has 7.7 Go of RAM and docker desktop is already running
next to it. With the default values everything becomes very slow.

minikube starts kubernetes 1.37.0 and our kubectl is the 1.34.1 of docker desktop. Kubernetes guarantees
only 1 minor version of difference and here we have 3, but all the commands of this lab worked. If one day
a command is strange we can use `minikube kubectl -- ...` which has the good version.

## Part 1 - the cluster

One single node called `minikube`, with the role `control-plane`. It's the particularity of minikube : the
same machine is the control-plane and the worker, in production they are separated.

> **Q.** Observe and explain what `kubectl top pods -A --sort-by cpu --sum=true` does.

`top pods` gives the **real** consumption of cpu and memory of each pod, and not what was asked in the
manifest. `-A` is for all the namespaces and not only `default`, `--sort-by cpu` sorts by cpu and
`--sum=true` adds the total at the bottom. The unit of the cpu is the millicore (`100m` = 0.1 core).

```text
NAMESPACE     NAME                               CPU(cores)   MEMORY(bytes)
kube-system   kube-apiserver-minikube            60m          207Mi
kube-system   etcd-minikube                      30m          31Mi
kube-system   kube-controller-manager-minikube   26m          49Mi
kube-system   kube-scheduler-minikube            20m          21Mi
kube-system   metrics-server-768f9f6999-5ht9b    16m          14Mi
kube-system   coredns-559f6c778d-tkfr5           11m          11Mi
kube-system   kindnet-8pvwc                      10m          7Mi
kube-system   storage-provisioner                3m           8Mi
kube-system   kube-proxy-6gs48                   2m           19Mi
                                                 ________     ________
                                                 175m         371Mi
```

The empty cluster already eats 175m of cpu (0.175 core on the 2 we gave, so 9%) and 371Mi of memory (12%),
only for itself. The biggest one is `kube-apiserver` and it's logic : everything passes by him, our
kubectl, the controllers, the scheduler, the kubelets. It's the bottleneck of a kubernetes cluster.

The components of `kube-system` and their role :

| Pod | Role |
|---|---|
| `etcd` | the key-value database, all the state of the cluster is inside |
| `kube-apiserver` | the door of entry, everything passes by him |
| `kube-scheduler` | decides on which node each pod goes |
| `kube-controller-manager` | compares in a loop the state we asked and the real state, and corrects |
| `kube-proxy` | the network rules on each node, it's him who makes the Services work |
| `coredns` | the internal dns |
| `kindnet` | the CNI, the network between the pods |
| `storage-provisioner` | added by minikube for the volumes |

Note : when we enable the metrics-server addon, `kubectl top` answers `error: Metrics API not available`
during one minute. The pod is `Running` but `0/1` READY, so it didn't pass its readiness probe yet and the
Service has no address behind it. **`Running` is not `Ready`** : Running means the container is started,
Ready means it answered its probe and it can receive the requests. We can wait properly with
`kubectl wait --for=condition=Ready`.

## Part 2 - the kubectl commands

```bash
kubectl create deployment kubernetes-bootcamp --image=gcr.io/google-samples/kubernetes-bootcamp:v1
```

The image is a `Debian GNU/Linux 8 (jessie)`, so a quite old base. The source code is `/server.js` and it
contains `www.listen(8080, ...)` : **the app listens on the port 8080**. The answer also has `" | v=1\n"`
written in hard, it's this one that will become `v=2` with the rolling update of the part 5.

Two things seen in `kubectl describe pod` :

- `Port: <none>` : the container declares no port and the app works anyway. To declare a port in a manifest
  is only documentation in kubernetes, it publishes nothing and it blocks nothing. What counts is the port
  where the process really listens. We need to know it's 8080 to fill the `service.yaml` of the part 6.
- `QoS Class: BestEffort` : no `requests` and no `limits` were defined, so this pod is the first one to be
  killed if the node misses memory. In production we always put requests and limits.

The `Events` at the bottom of the describe give all the history of the pod (`Scheduled`, `Pulling`,
`Pulled`, `Created`, `Started`). It's the first place to look when a pod doesn't start.

> **Q9.** Are you able to query the web app outside of the pod (from your local machine) ?

No. Inside the pod `curl localhost:8080` and `curl http://10.244.0.4:8080` both answer
`Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-4ptpr | v=1`, but from windows :

```text
PS> curl.exe --max-time 5 http://10.244.0.4:8080
curl: (28) Connection timed out after 5003 milliseconds
```

The `10.244.0.0/16` is the private network of the pods, managed by `kindnet`, and it exists only inside the
cluster. Our windows machine has no route to it. It's like the offices of a building : inside everybody can
call everybody, but from the street you can't call anybody directly. It's done on purpose, by default
nothing is exposed outside, we have to ask it. That's the goal of the part 3.

## Part 3 - expose the service outside the cluster

```bash
kubectl expose deployment kubernetes-bootcamp --type=NodePort --port=8080
```

```text
NAME                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
kubernetes-bootcamp   NodePort    10.98.218.216   <none>        8080:30654/TCP   2m8s
```

There are three ports and it's often badly understood :

| | Value | What it is |
|---|---|---|
| `targetPort` | 8080 | the port where the process listens in the container |
| `port` | 8080 | the port of the Service inside the cluster (same by default) |
| `nodePort` | 30654 | the port opened on the node, for the outside |

The **ClusterIP `10.98.218.216` never changes**, while the ip of the pods change at each recreation. That's
all the interest of a Service : one stable address in front of pods that are disposable. The `endpoint`
(here `10.244.0.4`) is the list, updated automatically, of the pods that match the `selector` of the
service.

`minikube ip` gives `192.168.49.2` but it's not reachable from windows with the docker driver, this ip
lives in the docker network. So we make a tunnel :

```bash
minikube service kubernetes-bootcamp --url
```

It gives an url like `http://127.0.0.1:64017` and **this command must stay running** : as soon as it gives
the hand back the tunnel dies. With this url the app finally answers from the host machine and from the web
browser.

## What is left to do

- Part 4 : scale to 5 pods, see the load balancing, scale down to 2
- Part 5 : rolling update v1 -> v2, then a v3 that doesn't exist on purpose, then rollback
- Part 6 : fill the `TO COMPLETE` of `lab-1/deployment.yaml` and `lab-1/service.yaml` and apply them
- Part 7 : teardown

## Notes for windows / powershell

The instructions of the lab are written in bash, we are in powershell :

| bash | powershell |
|---|---|
| `export VAR=$(cmd)` | `$VAR = cmd` |
| `for i in $(seq 10); do cmd; done` | `1..10 \| ForEach-Object { cmd }` |
| `while true; do cmd; sleep 0.5; done` | `while ($true) { cmd; Start-Sleep -Milliseconds 500 }` |
| `curl` | `curl.exe` (in powershell `curl` is an alias of `Invoke-WebRequest`) |

And after `winget install`, we have to restart vscode completely : opening a new terminal tab is not enough
because vscode keeps the environment it had at its launch, so the PATH doesn't have minikube.
