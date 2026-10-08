# Lab 5 - Kubernetes basics with minikube

Chapter `06.containerization-and-kubernetes`. This folder contains the 3 labs of the chapter :

- `lab-1` : kubernetes basics (parts 1 to 3 by Matt, parts 4 to 7 by Kylian), the completed manifests are
  in [`lab-1/`](./lab-1/)
- `lab-2` : ConfigMap and Secret, the files are in [`lab-2/`](./lab-2/)
- `lab-3` : Job and CronJob, the files are in [`lab-3/`](./lab-3/)

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

## Part 4 - scale up and down

The parts 4 to 7 were done on another machine (Kylian), so the parts 2 and 3 were replayed first to have the
deployment and the service again. The pod names and the tunnel port are not the same as above.

```bash
kubectl scale deployments/kubernetes-bootcamp --replicas=5
```

> **Q2.** Make sure that you have 5 pods running. Which command did you use ?

`kubectl get deployments` for the summary and `kubectl get pods -o wide` to see each pod with its ip :

```text
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
kubernetes-bootcamp   5/5     5            5           44s

NAME                                   READY   STATUS    RESTARTS   AGE   IP           NODE
kubernetes-bootcamp-5cc66bcc9b-fp4p9   1/1     Running   0          2s    10.244.0.6   minikube
kubernetes-bootcamp-5cc66bcc9b-jxdxd   1/1     Running   0          2s    10.244.0.7   minikube
kubernetes-bootcamp-5cc66bcc9b-lmxtd   1/1     Running   0          2s    10.244.0.5   minikube
kubernetes-bootcamp-5cc66bcc9b-rssxb   1/1     Running   0          2s    10.244.0.4   minikube
kubernetes-bootcamp-5cc66bcc9b-t6bxw   1/1     Running   0          44s   10.244.0.3   minikube
```

`5/5` in the `READY` column is the important number, not `Running` (see the note of the part 1). The 4 new
pods have the same prefix `5cc66bcc9b` as the first one : it's the hash of the ReplicaSet, scaling doesn't
create a new ReplicaSet, it only changes its number of replicas.

> **Q3.** Query the service several times. What is happening ? Why ?

```powershell
1..10 | ForEach-Object { curl.exe -s $APP_URL }
```

```text
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-rssxb | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-lmxtd | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-jxdxd | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-lmxtd | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-rssxb | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-jxdxd | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-fp4p9 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-jxdxd | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-t6bxw | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-fp4p9 | v=1
```

The requests are spread on the 5 pods : the Service does **load balancing**. We still call the same address,
but the Service now has 5 endpoints behind it :

```text
NAME                        ADDRESSTYPE   PORTS   ENDPOINTS                                      AGE
kubernetes-bootcamp-wwmrv   IPv4          8080    10.244.0.3,10.244.0.4,10.244.0.5 + 2 more...   24s
```

It's `kube-proxy` that writes the network rules on the node, and it chooses one endpoint **at random** for
each new connection. That's why it's not a perfect round robin (`jxdxd` answers 3 times, `t6bxw` only once).
On 10 requests it's not equal, on thousands it becomes equal. And it works because each `curl.exe` opens a
new connection, a web browser keeps the same connection and stays on the same pod.

Then we scale down to 2 :

```bash
kubectl scale deployments/kubernetes-bootcamp --replicas=2
```

```text
NAME                                   READY   STATUS        RESTARTS   AGE
kubernetes-bootcamp-5cc66bcc9b-fp4p9   1/1     Terminating   0          13s
kubernetes-bootcamp-5cc66bcc9b-jxdxd   1/1     Terminating   0          13s
kubernetes-bootcamp-5cc66bcc9b-lmxtd   1/1     Terminating   0          13s
kubernetes-bootcamp-5cc66bcc9b-rssxb   1/1     Running       0          13s
kubernetes-bootcamp-5cc66bcc9b-t6bxw   1/1     Running       0          55s
```

and 30 seconds later only 2 pods are left :

```text
NAME                                   READY   STATUS    RESTARTS   AGE
kubernetes-bootcamp-5cc66bcc9b-rssxb   1/1     Running   0          103s
kubernetes-bootcamp-5cc66bcc9b-t6bxw   1/1     Running   0          2m25s
```

Kubernetes removed the 3 youngest pods and kept the oldest ones. Why do the pods stay `Terminating` about
30 seconds ? Kubernetes sends `SIGTERM` to the process and waits up to `terminationGracePeriodSeconds`
(30s by default) before sending `SIGKILL`. The node app of the bootcamp doesn't handle `SIGTERM`, so it never
stops by itself and kubernetes waits the full 30 seconds. A real app should catch `SIGTERM`, finish its
current requests and exit. During this time the pod is already removed from the endpoints, so it receives
no new request.

## Part 5 - rolling update and rollback

We leave the loop running in a second terminal, with the time in front to see when things happen :

```powershell
while ($true) { "$(Get-Date -Format HH:mm:ss.f) $(curl.exe -s --max-time 2 $APP_URL)"; Start-Sleep -Milliseconds 500 }
```

```bash
kubectl set image deployments/kubernetes-bootcamp kubernetes-bootcamp=jocatalin/kubernetes-bootcamp:v2
```

> **Q3.** What happened to the responses ? Was the service interrupted ?

```text
12:34:16.3 Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-t6bxw | v=1
12:34:16.9 Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-rssxb | v=1
12:34:17.5 Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-rssxb | v=1
12:34:18.1 Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-7d5c7d7dc4-dsn4f | v=2
12:34:18.7 Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-7d5c7d7dc4-dsn4f | v=2
12:34:19.2 Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-7d5c7d7dc4-5tvwf | v=2
```

The answers go from `v=1` to `v=2` in about 2 seconds, and **the service was not interrupted** : on the 96
requests of the whole part (v1 -> v2 -> v3) there were 0 errors and 0 timeouts.

```text
Waiting for deployment "kubernetes-bootcamp" rollout to finish: 1 out of 2 new replicas have been updated...
Waiting for deployment "kubernetes-bootcamp" rollout to finish: 1 old replicas are pending termination...
deployment "kubernetes-bootcamp" successfully rolled out

NAME                             DESIRED   CURRENT   READY   AGE
kubernetes-bootcamp-5cc66bcc9b   0         0         0       2m40s
kubernetes-bootcamp-7d5c7d7dc4   2         2         2       3s
```

Why there is no cut : changing the image changes the pod template, so the deployment creates a **new
ReplicaSet** (`7d5c7d7dc4`) and moves the pods from the old one to the new one, little by little. The default
strategy is `RollingUpdate` with `maxSurge: 25%` and `maxUnavailable: 25%`. With 2 replicas, the surge is
rounded up (1 extra pod allowed) and the unavailable is rounded down (0 pod allowed to be missing). So
kubernetes creates 1 new pod, waits for it to be **Ready**, and only then kills 1 old pod, and again. At
every moment there are at least 2 ready pods behind the Service. The old ReplicaSet is not deleted, it stays
with 0 replicas : that's what makes the rollback possible.

Then the v3, that doesn't exist on purpose :

```bash
kubectl set image deployments/kubernetes-bootcamp kubernetes-bootcamp=jocatalin/kubernetes-bootcamp:v3
```

> **Q5.** List all the running pods, what is happening here ? Is the service still responding ? Why ?

```text
NAME                                   READY   STATUS             RESTARTS   AGE
kubernetes-bootcamp-795cf895df-m7qnl   0/1     ImagePullBackOff   0          17s
kubernetes-bootcamp-7d5c7d7dc4-5tvwf   1/1     Running            0          30s
kubernetes-bootcamp-7d5c7d7dc4-dsn4f   1/1     Running            0          33s

NAME                             DESIRED   CURRENT   READY   AGE
kubernetes-bootcamp-5cc66bcc9b   0         0         0       3m10s
kubernetes-bootcamp-795cf895df   1         1         0       17s
kubernetes-bootcamp-7d5c7d7dc4   2         2         2       33s

NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
kubernetes-bootcamp   2/2     1            2           3m10s
```

The `describe` of the new pod gives the reason :

```text
Warning  Failed  kubelet  Failed to pull image "jocatalin/kubernetes-bootcamp:v3": rpc error: code = NotFound
         desc = failed to pull and unpack image "docker.io/jocatalin/kubernetes-bootcamp:v3": ... not found
Warning  Failed  kubelet  Error: ErrImagePull
Normal   BackOff kubelet  Back-off pulling image "jocatalin/kubernetes-bootcamp:v3"
Warning  Failed  kubelet  Error: ImagePullBackOff
```

The new pod can't download its image, so it's stuck in `ImagePullBackOff` (kubernetes retries the pull,
waiting longer each time). **The service still responds, with `v=2`.** It's the same rule as for v2 : the
rolling update only kills an old pod once a new one is Ready. The v3 pod is never Ready, so the 2 v2 pods are
never killed, and the Service sends traffic only to the Ready pods. The deployment says `2/2` available and
`1` up-to-date : the rollout is blocked in the middle, but the users see nothing.

`kubectl rollout status` waits forever (here we put `--timeout=10s`). Kubernetes does **not** roll back by
itself : after `progressDeadlineSeconds` (600s by default) it only marks the deployment as failed. It's to us
to cancel :

```bash
kubectl rollout undo deployments/kubernetes-bootcamp
```

```text
deployment.apps/kubernetes-bootcamp rolled back
deployment "kubernetes-bootcamp" successfully rolled out
```

> **Q7.** Roll back the service to the image we first chose in part 2.

```text
PS> kubectl rollout history deployments/kubernetes-bootcamp
REVISION  CHANGE-CAUSE
1         <none>
3         <none>
4         <none>

PS> kubectl rollout history deployments/kubernetes-bootcamp --revision=1
    Image:	gcr.io/google-samples/kubernetes-bootcamp:v1
```

```bash
kubectl rollout undo deployments/kubernetes-bootcamp --to-revision=1
```

```text
PS> kubectl get deploy kubernetes-bootcamp -o jsonpath='{.spec.template.spec.containers[0].image}'
gcr.io/google-samples/kubernetes-bootcamp:v1
PS> curl.exe -s $APP_URL
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-5cc66bcc9b-ns85l | v=1
```

Three things to understand in the history :

- The revision 2 disappeared. The undo of v3 didn't go "back" to revision 2, it copied the template of the
  revision 2 into a **new** revision 4. A revision number is always the newest version of a given template.
  After the `--to-revision=1` the history is `3, 4, 5` for the same reason.
- The new v1 pods have the prefix `5cc66bcc9b` again, the ReplicaSet of the part 2. Kubernetes didn't create
  a new ReplicaSet, it scaled the old one back from 0 to 2. Same template = same hash = same ReplicaSet.
- `CHANGE-CAUSE` is `<none>` everywhere : with `kubectl annotate deployment ... kubernetes.io/change-cause="..."`
  we could write why each version was made, it would make the history much more readable.

## Part 6 - deploy with the yaml manifests

```bash
kubectl delete service kubernetes-bootcamp
kubectl delete deployment kubernetes-bootcamp
```

**`TO COMPLETE #1`** of [`lab-1/deployment.yaml`](./lab-1/deployment.yaml), the container :

```yaml
      containers:
      - name: kubernetes-bootcamp
        image: gcr.io/google-samples/kubernetes-bootcamp:v1
        ports:
        - containerPort: 8080
```

The image is the one of the part 2. As Matt explained, `containerPort` is only documentation, the app would
work without it, but it says to the reader of the file where the app listens.

> **Q4.** Are the pods running ?

Yes :

```text
PS> kubectl apply -f deployment.yaml
deployment.apps/kubernetes-bootcamp created

NAME                                       READY   STATUS    RESTARTS   AGE
pod/kubernetes-bootcamp-576b7cbb77-9kkb5   1/1     Running   0          0s
```

The ReplicaSet hash is `576b7cbb77` and not `5cc66bcc9b` like with `kubectl create deployment`, even with the
same image : we added `containerPort` in the template, so the template is different, so the hash is different.

**The blanks** of [`lab-1/service.yaml`](./lab-1/service.yaml) :

```yaml
  selector:
    app: kubernetes-bootcamp
  ports:
    - port: 8080
```

The `selector` must be **exactly** the label put on the pods by the `template` of the deployment, it's the
only link between the two objects. If there is a typo, the Service is created without error but with 0
endpoints, and every request fails. We didn't write `targetPort` : by default it's the same as `port`, so
8080, where the app listens.

> **Q6.** Can you access the service through `curl` or your web browser ?

Yes, after a new tunnel. Careful, the Service is now called `kubernetes-bootcamp-service` and not
`kubernetes-bootcamp` anymore, so the command changes :

```text
PS> kubectl get svc kubernetes-bootcamp-service
NAME                          TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
kubernetes-bootcamp-service   NodePort   10.108.216.73   <none>        8080:31122/TCP   0s

PS> minikube service kubernetes-bootcamp-service --url
http://127.0.0.1:63860

PS> curl.exe -s http://127.0.0.1:63860
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-9kkb5 | v=1
```

**`TO COMPLETE #2`**, 3 replicas :

```yaml
spec:
  replicas: 3
```

> **Q8.** Query the service several times. Are you hitting different replicas ?

```text
PS> kubectl apply -f deployment.yaml
deployment.apps/kubernetes-bootcamp configured

NAME                                ADDRESSTYPE   PORTS   ENDPOINTS                             AGE
kubernetes-bootcamp-service-f7kxw   IPv4          8080    10.244.0.13,10.244.0.15,10.244.0.14   19s

PS> 1..10 | ForEach-Object { curl.exe -s http://127.0.0.1:63860 }
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-9kkb5 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-2c975 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-2c975 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-2c975 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-9kkb5 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-2c975 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-2c975 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-2c975 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-9kkb5 | v=1
Hello Kubernetes bootcamp! | Running on: kubernetes-bootcamp-576b7cbb77-2c975 | v=1
```

Yes, different replicas answer. The third one (`xzcf5`) is in the endpoints but was not chosen in these
10 requests : it's the random choice of `kube-proxy` again, same as in part 4.

What is interesting here is the word **`configured`** : the second `apply` did not recreate the deployment,
it compared the file with what runs in the cluster and changed only the difference. The pod `9kkb5` was kept,
only 2 pods were added. And if we apply the same file again, nothing happens :

```text
PS> kubectl apply -f deployment.yaml
deployment.apps/kubernetes-bootcamp unchanged
```

It's the big difference with the commands of the parts 2 to 5. `kubectl scale` or `kubectl set image` say
"do this action", the yaml says "this is the state I want", and kubernetes finds alone the actions to reach
it. The file is in git, so the state of the cluster is versioned, reviewed and can be rebuilt from zero with
one command. With the imperative commands, the state only exists in the cluster and in our shell history.

## Part 7 - teardown

```text
PS> kubectl delete -f service.yaml
service "kubernetes-bootcamp-service" deleted from default namespace
PS> kubectl delete -f deployment.yaml
deployment.apps "kubernetes-bootcamp" deleted from default namespace
PS> kubectl get all
NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   5m43s
```

Only the `kubernetes` service is left, it's the service of the API server itself, it's always there.
`minikube stop` was done at the end of the lab-3, because the labs 2 and 3 use the same cluster.

# Lab 2 - ConfigMap and Secret

The files are in [`lab-2/`](./lab-2/). The idea : the image must be the same in dev, test and prod, so the
configuration has to live **outside** the image. A ConfigMap is for normal config, a Secret for passwords
and keys.

## Creating ConfigMaps

The 3 methods give the same kind of object, but not the same keys :

```text
PS> kubectl -n lab-configmap-secret get configmap
NAME                   DATA   AGE
data-paths             3      1s
data-platform-config   5      0s
kube-root-ca.crt       1      1s
pipeline-config        1      1s
```

- `--from-file` (`pipeline-config`) : `DATA 1`. The whole file is **one** key, called like the file
  (`pipeline-config.properties`), and the 9 lines are its value. Kubernetes doesn't parse the `.properties`.
  If we wanted 9 keys, it's `--from-env-file`.
- `--from-literal` (`data-paths`) : 3 keys, one per `--from-literal`. Quick for a test, but nothing is written
  anywhere, we can't rebuild it.
- the yaml manifest (`data-platform-config`) : 5 keys, 3 simple values and 2 whole files (`application.yaml`
  and `table_mappings.csv`). It's the good method because the file goes in git, like in the part 6 of lab-1.

`kube-root-ca.crt` is created automatically in each namespace, it's the certificate to talk to the API server.

The values are always strings : in the yaml we must write `spark_workers: "4"` with the quotes, without them
the yaml would be a number and the API server refuses it.

## Creating Secrets

```text
PS> kubectl -n lab-configmap-secret get secret ceph-credentials -o yaml
data:
  access-key: QUtJQUlP...REDACTED
  secret-key: d0phbHJY...REDACTED
```

It looks hidden but it's only base64, anyone who can read the Secret gets the value in one command.
(The values are cut in this README : they are the fake example keys of AWS, but GitHub push protection
recognizes them and refuses the push, which is a good illustration of the point.) In
powershell there is no `base64 -d`, we used .NET :

```text
PS> $b64 = kubectl -n lab-configmap-secret get secret ceph-s3-credentials -o jsonpath='{.data.secret-key}'
PS> [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b64))
wJalr...REDACTED
```

and with `jq` (installed with `winget install jqlang.jq`, then restart the terminal) :

```text
access-key=AKIA...REDACTED
bucket=data-platform-bronze
endpoint=ceph-rgw.ceph-storage.svc.cluster.local:7480
secret-key=wJalr...REDACTED
```

base64 is an **encoding**, not an encryption : its goal is to put binary data (a certificate, a key file) in
a yaml, not to protect it. The protection of a Secret comes from elsewhere : the RBAC (who has the right to
read Secrets), the encryption of etcd on the disk, and the fact that the kubelet keeps it in memory (see
below).

**Something we didn't expect**, in the Secret created with `kubectl apply` :

```text
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Secret",...,"stringData":{"access-key":"AKIA...REDACTED",...,
      "secret-key":"wJalr...REDACTED"},"type":"Opaque"}
```

To be able to compute the difference at the next `apply` (the `configured` / `unchanged` of lab-1),
kubectl saves the whole file in an annotation. With `stringData`, it means the secret is copied **in clear
text, not even in base64** in the annotation. For a Secret it's better to use `kubectl apply --server-side`
or `kubectl create`, which don't write this annotation.

For the same reason we did **not** commit `secret-ceph-credentials.yaml` and `s3-credentials.txt` (they are
in the [`.gitignore`](./lab-2/.gitignore)). The keys of the lab are the fake example keys of AWS, but the
habit is the important thing : once a secret is in the git history, removing the file is not enough, it
stays in the old commits. In a real project : Sealed Secrets or a vault, like the lab says.

## Using them in pods

**As environment variables** (`pod-with-configmap.yaml`) :

```text
PS> kubectl -n lab-configmap-secret exec spark-app -- env
LOG_LEVEL=INFO
SPARK_WORKERS=4
batch_size=1000
log_level=INFO
spark_workers=4
table_mappings.csv=source_table,bronze_path,silver_layer
application.yaml=# Data Platform Application Config
...
```

`env` with `configMapKeyRef` chooses one key and gives it the name we want (`LOG_LEVEL`). `envFrom` takes
**all** the keys with their own name, so we have both `LOG_LEVEL` and `log_level` (the names are case
sensitive), and even 2 variables called `application.yaml` and `table_mappings.csv` that contain whole
files. It works but it's not clean : `envFrom` is good for a ConfigMap made for it (like `etl-config` in
lab-3), not for a ConfigMap that mixes values and files.

The Secret works the same way (`pod-with-secret.yaml`) :

```text
PS> kubectl -n lab-configmap-secret logs ceph-connector
Access Key: AKIA...REDACTED
```

The pod has `restartPolicy: Never` because its command finishes : with the default `Always`, kubernetes would
restart it again and again (`CrashLoopBackOff`) even if it ends with success. Here it's `Completed`.

**As files** (`pod-with-configmap-volume.yaml`) :

```text
PS> kubectl -n lab-configmap-secret exec spark-config-reader -- ls -la /etc/config/
drwxr-xr-x    2 root     root          4096 Oct  8 10:38 ..2026_10_08_10_38_20.344901959
lrwxrwxrwx    1 root     root            31 Oct  8 10:38 ..data -> ..2026_10_08_10_38_20.344901959
lrwxrwxrwx    1 root     root            23 Oct  8 10:38 application.yaml -> ..data/application.yaml
lrwxrwxrwx    1 root     root            17 Oct  8 10:38 tables.csv -> ..data/tables.csv
```

With `items` we chose only 2 keys and renamed `table_mappings.csv` into `tables.csv`. The files are links to
a folder with a date : it's how kubernetes updates them. We tested it, we changed the ConfigMap while the 2
pods were running :

```powershell
kubectl -n lab-configmap-secret patch configmap data-platform-config --type merge -p '{\"data\":{\"table_mappings.csv\":\"source_table,bronze_path,silver_layer\nusers,/data/bronze/users,clean_users\n\"}}'
```

About one minute later, the file in the volume changed alone (new folder `..2026_10_08_10_39_38...`, the
link `..data` moved to it, so the change is atomic) :

```text
PS> kubectl -n lab-configmap-secret exec spark-config-reader -- cat /etc/config/tables.csv
source_table,bronze_path,silver_layer
users,/data/bronze/users,clean_users
```

but the environment variable of `spark-app` still had the old value :

```text
PS> kubectl -n lab-configmap-secret exec spark-app -- sh -c 'env | grep -A1 table_mappings'
table_mappings.csv=source_table,bronze_path,silver_layer
customers,/data/bronze/customers,deduplicated_customers
```

The environment of a process is fixed when it starts, kubernetes can't change it after. So : **a volume
follows the changes, an env variable needs a restart of the pod** (for a deployment,
`kubectl rollout restart`). And the app must re-read its file to see the change.

**The Secret as files** (`pod-with-secret-volume.yaml`) :

```text
PS> kubectl -n lab-configmap-secret exec ceph-connector-secure -- ls -laL /etc/ceph-credentials/
-rw-------    1 root     root           116 Oct  8 10:38 s3-credentials.txt

PS> kubectl -n lab-configmap-secret exec ceph-connector-secure -- touch /etc/ceph-credentials/x
touch: /etc/ceph-credentials/x: Read-only file system

PS> kubectl -n lab-configmap-secret exec ceph-connector-secure -- mount | grep ceph-credentials
tmpfs on /etc/ceph-credentials type tmpfs (ro,relatime,size=8018144k,noswap)
```

- `-rw-------` is the `defaultMode: 0600`, only the owner can read.
- `ro` is the `readOnly: true`, the app can't modify or replace the credentials.
- `tmpfs` is the interesting one : the Secret is in the **RAM** of the node, it's never written on its disk,
  so it disappears when the pod is stopped. The ConfigMap volume above is a normal folder on the disk of the node.

For a Secret, a file is better than an env variable : env variables are easy to leak (a crash dump, a
`printenv` in a debug log, the child processes inherit them), a file in `tmpfs` with `0600` is not.

```bash
kubectl delete namespace lab-configmap-secret
```

Deleting the namespace deletes everything inside it (pods, ConfigMaps, Secrets) in one command, that's why
each lab uses its own namespace.

# Lab 3 - Job and CronJob

The files are in [`lab-3/`](./lab-3/). A Deployment must run **forever** (if the process stops, it's
restarted). A Job must run **until it ends with success**, then stop. A CronJob creates a Job at fixed times.

The image was pulled before (`minikube image pull python:3.13-slim`), otherwise the download time is counted
in the deadlines of the Jobs.

## Simple Job

```text
NAME              STATUS     COMPLETIONS   DURATION   AGE
data-import-job   Complete   1/1           6s         6s

PS> kubectl -n lab-job-cronjob logs -l job-name=data-import-job
Starting data import...
Processing 1000 records...
Import completed!

NAME                    READY   STATUS      RESTARTS   AGE
data-import-job-96699   0/1     Completed   0          7s
```

The pod stays `Completed` and is not deleted : we can still read its logs after the end.

## Job with retry

> How many Pods were created ? Why are they kept after the failure ?

```text
NAME                       STATUS   CREATED
data-transform-job-m8cm4   Failed   2026-10-08T11:50:20Z
data-transform-job-4mw7b   Failed   2026-10-08T11:50:31Z
data-transform-job-ffkr7   Failed   2026-10-08T11:50:51Z
data-transform-job-cf292   Failed   2026-10-08T11:51:32Z
```

**4 pods** : 1 first try + `backoffLimit: 3` retries. With `restartPolicy: Never`, kubernetes doesn't restart
the container in the same pod, it creates a **new pod** for each try. Look at the times : +11s, +20s, +41s,
the wait doubles each time (exponential back-off, 10s, 20s, 40s...). It's on purpose : if the error comes
from something outside (a database that restarts), retrying 100 times per second makes things worse.

The failed pods are kept to be able to **debug** : each one has its logs, and it's the only place where we
can read why it failed :

```text
[pod/data-transform-job-m8cm4/transform] Transforming records...
[pod/data-transform-job-m8cm4/transform] ERROR: Validation failed!
```

They are deleted with the Job (or automatically with `ttlSecondsAfterFinished`, see the parallel Job).

> What is the reason of the Job failure in the `describe` output ?

```text
Backoff Limit:            3
Active Deadline Seconds:  300s
Pods Statuses:            0 Active (0 Ready) / 0 Succeeded / 4 Failed
  Normal   SuccessfulCreate      76s   job-controller  Created pod: data-transform-job-m8cm4
  Normal   SuccessfulCreate      65s   job-controller  Created pod: data-transform-job-4mw7b
  Normal   SuccessfulCreate      45s   job-controller  Created pod: data-transform-job-ffkr7
  Normal   SuccessfulCreate      4s    job-controller  Created pod: data-transform-job-cf292
  Warning  BackoffLimitExceeded  1s    job-controller  Job has reached the specified backoff limit
```

**`BackoffLimitExceeded`** : the 4 tries failed, kubernetes stops trying.

> Change `activeDeadlineSeconds` to `10`, delete and re-apply the Job. What is the new reason ?

```text
Active Deadline Seconds:  10s
Pods Statuses:            0 Active (0 Ready) / 0 Succeeded / 1 Failed
  Normal   SuccessfulCreate  10s   job-controller  Created pod: data-transform-job-55j22
  Warning  DeadlineExceeded  0s    job-controller  Job was active longer than specified deadline
```

**`DeadlineExceeded`** and only **1 pod**. The first try fails, the back-off says "wait 10s", and at 10s the
Job is already out of time, so no retry. `activeDeadlineSeconds` is a limit on the time of the **whole Job**
(all the tries together), `backoffLimit` is a limit on the number of tries : the first one reached wins. In a
pipeline it's important : a Job blocked forever (a network call without timeout) would never fail with
`backoffLimit` only, the deadline protects from it.

Note : our first try of this part was false. The laptop went to sleep (lid closed) from 12:42 to 13:49 during
the Job. The cluster was frozen, at the wake up the 300 seconds were over, so we saw only 3 pods and
`DeadlineExceeded`. Keep the laptop open during the labs with timers.

## Parallel Job

```text
NAME                       READY   STATUS    RESTARTS   AGE   IP
batch-export-job-0-95x9f   1/1     Running   0          2s    10.244.0.29
batch-export-job-1-txqrn   1/1     Running   0          2s    10.244.0.30
batch-export-job-2-h8sws   1/1     Running   0          2s    10.244.0.31
batch-export-job-3-4tz9q   1/1     Running   0          2s    10.244.0.32

NAME               STATUS     COMPLETIONS   DURATION   AGE
batch-export-job   Complete   4/4           10s        10s

[pod/batch-export-job-0-95x9f/export] Pod batch-export-job-0: Exporting shard 0 (users with id % 4 == 0)...
[pod/batch-export-job-0-95x9f/export] Pod batch-export-job-0: Shard 0 export completed!
[pod/batch-export-job-1-txqrn/export] Pod batch-export-job-1: Exporting shard 1 (users with id % 4 == 1)...
...
[pod/batch-export-job-3-4tz9q/export] Pod batch-export-job-3: Shard 3 export completed!
```

The 4 pods start at the same second (`11:52:50` for all of them) and the Job takes 10s for 4 x 5s of work.
With `completionMode: Indexed` each pod has a number (0 to 3) in its name and in `JOB_COMPLETION_INDEX`, so
each one knows its part of the data without talking to the others. It's the same idea as the partitions in
Spark. And if the pod 2 fails, kubernetes recreates a pod **with the index 2**, so no shard is lost or done
twice. In the logs the `HOSTNAME` is `batch-export-job-0` and not the full pod name : for an indexed Job the
hostname is stable, it doesn't depend on the random suffix.

## CronJob

```text
NAME                        SCHEDULE      TIMEZONE       SUSPEND   ACTIVE   LAST SCHEDULE   AGE
bronze-to-silver-pipeline   */2 * * * *   <none>         False     1        1s              2m26s
daily-backup                0 2 * * *     Europe/Paris   False     0        <none>          2m25s
etl-bronze-to-silver        */5 * * * *   <none>         False     0        61s             2m25s

NAME                                 STATUS     COMPLETIONS   DURATION   AGE
bronze-to-silver-pipeline-29857674   Complete   1/1           4s         2m1s
bronze-to-silver-pipeline-29857676   Running    0/1           1s         1s
etl-bronze-to-silver-29857675        Complete   1/1           3s         61s
```

```text
PS> kubectl -n lab-job-cronjob logs job/bronze-to-silver-pipeline-29857674
[2026-10-08 11:54:00.726661] Bronze→Silver ETL started...
[2026-10-08 11:54:02.727058] Completed! 500 records processed
```

- The suffix of the Jobs is not random : `29857674` is the number of **minutes since 1970** of the planned
  time (29857674 min = 2026-10-08 11:54 UTC). So 2 runs of the same CronJob can never have the same name,
  and kubernetes can't create twice the Job of the same minute.
- The times in the logs are in UTC (`11:54`) while it was 13:54 in Paris. Without `timeZone` the schedule is
  in the time zone of the controller manager, so UTC : `0 2 * * *` without `timeZone` would run at 4 AM in
  summer in Paris. That's why `daily-backup` has `timeZone: Europe/Paris`.
- `concurrencyPolicy: Forbid` : if one run is still running when the next one should start, the next one is
  skipped. For an ETL it's important, 2 runs writing the same silver table at the same time can corrupt it.

## Monitoring, suspend and resume

```text
PS> kubectl -n lab-job-cronjob describe job data-import-job
Completed At:     Thu, 08 Oct 2026 12:41:13 +0200
Duration:         6s
Pods Statuses:    0 Active (0 Ready) / 1 Succeeded / 0 Failed
```

We suspended the CronJob at 13:57 and waited after 13:58, the time of the next run :

```text
checked at 13:58:23
NAME                        SCHEDULE      TIMEZONE   SUSPEND   ACTIVE   LAST SCHEDULE   AGE
bronze-to-silver-pipeline   */2 * * * *   <none>     True      0        2m23s           4m48s

bronze-to-silver-pipeline-29857674   Complete   1/1           4s         4m23s
bronze-to-silver-pipeline-29857676   Complete   1/1           5s         2m23s
```

No Job at 13:58, the suspend works. Then we resumed at 13:58:24 and checked 2 minutes later :

```text
checked at 14:00:24
bronze-to-silver-pipeline-29857676   Complete   1/1           5s         4m25s
bronze-to-silver-pipeline-29857678   Complete   1/1           6s         2m1s
bronze-to-silver-pipeline-29857680   Complete   1/1           5s         25s
```

Two things we didn't expect :

- `...678` is the run of **13:58**, the one that was skipped, and it was created at 13:58:24, just after the
  resume. When a CronJob is resumed, kubernetes runs the last missed schedule. It's controlled by
  `startingDeadlineSeconds` : not set here, so the missed run is always done. For a backup it's good, for a
  pipeline that must not run outside its hour, we should put a small `startingDeadlineSeconds`.
- `...674` disappeared : `successfulJobsHistoryLimit: 3` keeps only the 3 last successful Jobs. Without this
  limit, a CronJob every 2 minutes would leave 720 Jobs per day in the cluster.

## Data pipeline scenario

```text
PS> kubectl -n lab-job-cronjob create job etl-manual-run --from=cronjob/etl-bronze-to-silver
PS> kubectl -n lab-job-cronjob logs job/etl-manual-run
[2026-10-08T11:53:38.137149] ETL: bronze -> silver
[2026-10-08T11:53:38.137149] Batch size: 1000
[2026-10-08T11:53:38.137149] Reading, validating, deduplicating...
[2026-10-08T11:53:38.137149] Writing to silver layer...
[2026-10-08T11:53:38.137149] Completed!
```

It joins the 2 labs : the parameters come from the ConfigMap `etl-config` (`envFrom`, a good use this time
because the ConfigMap is made only of env variables), the code is in the CronJob. To change the batch size,
we change the ConfigMap and the next run uses it, no new image. `create job --from=cronjob/...` is very
useful : it tests the exact template of the CronJob now, without waiting for its schedule (the planned run
of 11:55 gave the same result).

The ETL also has `resources` : `requests` is what the scheduler reserves on the node, `limits.memory` is the
maximum, above it the container is killed (`OOMKilled`). Like Matt said in part 2, without them the pod is
`BestEffort` and is the first one killed when the node misses memory.

```text
PS> kubectl delete namespace lab-job-cronjob
namespace "lab-job-cronjob" deleted
PS> kubectl get namespace lab-job-cronjob
Error from server (NotFound): namespaces "lab-job-cronjob" not found
PS> minikube stop
* 1 nœud arrêté.
```

## Notes for windows / powershell

The instructions of the lab are written in bash, we are in powershell :

| bash | powershell |
|---|---|
| `export VAR=$(cmd)` | `$VAR = cmd` |
| `for i in $(seq 10); do cmd; done` | `1..10 \| ForEach-Object { cmd }` |
| `while true; do cmd; sleep 0.5; done` | `while ($true) { cmd; Start-Sleep -Milliseconds 500 }` |
| `curl` | `curl.exe` (in powershell `curl` is an alias of `Invoke-WebRequest`) |

And after `winget install`, we have to restart vscode completely : opening a new terminal tab is not enough
because vscode keeps the environment it had at its launch, so the PATH doesn't have minikube. Same thing
for `jq`. Without restarting, the full path works : `& "C:\Program Files\Kubernetes\Minikube\minikube.exe"`.

`base64 -d` doesn't exist in powershell, to decode a Secret :
`[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b64))`.

Docker Desktop crashed at the start on Kylian's machine with `initializing Inference manager: listening on
unix://...\Docker\run\dockerInference: remove ...: The file cannot be accessed by the system`. These are
socket files left by an old session that windows can't delete. Fix : quit Docker Desktop, `wsl --shutdown`,
rename the folders `%LOCALAPPDATA%\Docker\run` and `%LOCALAPPDATA%\docker-secrets-engine` (add `.old` for
example), restart Docker Desktop. It recreates them clean.

If the laptop goes to sleep, the cluster is frozen and all the timers (deadlines of the Jobs, schedules of
the CronJobs) are wrong at the wake up, see the lab 3.
