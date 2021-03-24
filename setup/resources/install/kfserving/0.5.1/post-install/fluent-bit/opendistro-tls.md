# Fluent-bit Output to Open Distro for Elasticsearch

## Fork Secrets to authenticate

```bash
NAMESPACE="logging"
ES_NAMESPACE="elasticsearch"

# elasticsearch-rest-certs
kubectl -n ${NAMESPACE} apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: elasticsearch-rest-certs
type: kubernetes.io/tls
data:
  ca.crt: "$(kubectl -n ${ES_NAMESPACE} get secrets elasticsearch-rest-certs -o jsonpath='{.data.ca\.crt}')"
  tls.crt: "$(kubectl -n ${ES_NAMESPACE} get secrets elasticsearch-rest-certs -o jsonpath='{.data.tls\.crt}')"
  tls.key: "$(kubectl -n ${ES_NAMESPACE} get secrets elasticsearch-rest-certs -o jsonpath='{.data.tls\.key}')"
EOF
```

## Change `custom-values.yaml`

### `extraVolumes` and `extraVolumeMounts`

```yaml
extraVolumes:
- name: elasticsearch-rest-certs
  secret:
    secretName: elasticsearch-rest-certs
    items:
    - key: tls.crt
      path: elk-rest-crt.pem
    - key: tls.key
      path: elk-rest-key.pem
    - key: ca.crt
      path: elk-rest-root-ca.pem

extraVolumeMounts:
- name: elasticsearch-rest-certs
  mountPath: /usr/share/elasticsearch/config
  readOnly: true
```

### `config.outputs`

```yaml
config:
  ## https://docs.fluentbit.io/manual/pipeline/outputs
  outputs: |
    [OUTPUT]
        Name                es
        Match               *
        # Match               kube.*
        Host                ${FLUENT_ELASTICSEARCH_HOST}
        Port                ${FLUENT_ELASTICSEARCH_PORT}
        # HTTP_User           ${ELASTICSEARCH_USERNAME}
        # HTTP_Passwd         ${ELASTICSEARCH_PASSWORD}
        Index               fluent-bit
        Type                _doc
        Logstash_Format     On
        # Logstash_Prefix     node
        Logstash_Prefix     ${record['kubernetes']['namespace_name']}
        Logstash_Prefix_Key $kubernetes['labels']['app']
        Logstash_DateFormat %Y.%m.%d
        Time_Key            @timestamp
        Time_Key_Format     %Y-%m-%dT%H:%M:%S
        Replace_Dots        On
        Retry_Limit         False
        tls                 on
        tls.verify          on
        tls.debug           1
        tls.ca_file         /usr/share/elasticsearch/config/elk-rest-root-ca.pem
        tls.crt_file        /usr/share/elasticsearch/config/elk-rest-crt.pem
        tls.key_file        /usr/share/elasticsearch/config/elk-rest-key.pem

    [OUTPUT]
        Name                es-airuntime
        Match               kube.airuntime-*
        Host                ${FLUENT_ELASTICSEARCH_HOST}
        Port                ${FLUENT_ELASTICSEARCH_PORT}
        Index               fluent-bit
        Type                _doc
        Logstash_Format     On
        Logstash_Prefix     ${record['kubernetes']['namespace_name']}
        Logstash_Prefix_Key $kubernetes['labels']['app']
        Logstash_DateFormat %Y.%m.%d
        Time_Key            @timestamp
        Time_Key_Format     %Y-%m-%dT%H:%M:%S
        Replace_Dots        On
        Retry_Limit         False
        tls                 on
        tls.verify          on
        tls.debug           1
        tls.ca_file         /usr/share/elasticsearch/config/elk-rest-root-ca.pem
        tls.crt_file        /usr/share/elasticsearch/config/elk-rest-crt.pem
        tls.key_file        /usr/share/elasticsearch/config/elk-rest-key.pem

    [OUTPUT]
        Name                es-airuntime
        Match               kube.airuntime-*
        Host                ${FLUENT_ELASTICSEARCH_HOST}
        Port                ${FLUENT_ELASTICSEARCH_PORT}
        Index               fluent-bit
        Type                _doc
        Logstash_Format     On
        # Logstash_Prefix     $kubernetes['labels']['app']
        Logstash_Prefix     ${record['kubernetes']['namespace_name']}
        Logstash_DateFormat %Y.%m.%d
        Time_Key            @timestamp
        Time_Key_Format     %Y-%m-%dT%H:%M:%S
        Replace_Dots        On
        Retry_Limit         False
        tls                 on
        tls.verify          on
        tls.debug           1
        tls.ca_file         /usr/share/elasticsearch/config/elk-rest-root-ca.pem
        tls.crt_file        /usr/share/elasticsearch/config/elk-rest-crt.pem
        tls.key_file        /usr/share/elasticsearch/config/elk-rest-key.pem
```

## Upgrade the existing release

```bash
helm upgrade fluent-bit fluent/fluent-bit \
  --namespace ${NAMESPACE} \
  --values=custom-values.yaml \
  > install_fluent-bit.log
```
