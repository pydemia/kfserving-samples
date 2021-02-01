

```bash
curl -fsSL https://github.com/jetstack/cert-manager/releases/download/v1.1.0/cert-manager.yaml -O && \
  kubectl apply -f cert-manager.yaml
```

:warning: It can be hung due to deeply nested CRDs.
[Ref.](https://cert-manager.io/next-docs/installation/upgrading/upgrading-0.15-0.16/)

Update your `kubectl` over `1.20` is recommended.

```bash
curl -LO https://dl.k8s.io/release/v1.20.0/bin/linux/amd64/kubectl && \
  chmod +x kubectl && \
  mkdir -p $HOME/.local/bin && \
  mv kubectl $HOME/.local/bin/kubectl
```
