```bash
$ kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.1.0/cert-manager.yaml
$ kubectl get pods --all-namespaces

cert-manager         cert-manager-5597cff495-wsh25                0/1     ErrImagePull        0          11s

$ kubectl describe pod cert-manager-5597cff495-wsh25 -n cert-manager
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  32s                default-scheduler  Successfully assigned cert-manager/cert-manager-5597cff495-wsh25 to kind-control-plane
  Normal   Pulling    15s (x2 over 31s)  kubelet            Pulling image "quay.io/jetstack/cert-manager-controller:v1.1.0"
  Warning  Failed     15s (x2 over 31s)  kubelet            Failed to pull image "quay.io/jetstack/cert-manager-controller:v1.1.0": rpc error: code = Unknown desc = failed to pull and unpack image "quay.io/jetstack/cert-manager-controller:v1.1.0": failed to resolve reference "quay.io/jetstack/cert-manager-controller:v1.1.0": failed to do request: Head https://quay.io/v2/jetstack/cert-manager-controller/manifests/v1.1.0: x509: certificate signed by unknown authority
  Warning  Failed     15s (x2 over 31s)  kubelet            Error: ErrImagePull
  Normal   BackOff    4s (x2 over 31s)   kubelet            Back-off pulling image "quay.io/jetstack/cert-manager-controller:v1.1.0"
  Warning  Failed     4s (x2 over 31s)   kubelet            Error: ImagePullBackOff
```


```bash
# Locate `CUSTOM_CA.crt` into /usr/local/share/ca-certificates/
cp ./CUSTOM_CA.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

:warning:
You have to do that on every cluster node: all masters and workers. Kubernetes simply relies on CAs installed on underlying operating system.

https://serverfault.com/questions/1020310/how-do-i-add-certificates-to-kubernetes-to-allow-images-to-be-pulled-from-a-cust