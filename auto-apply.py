import os
import tempfile
from kubernetes import client, config, watch
from kubernetes.utils import create_from_yaml

APPLY_YAML_DATA =  os.getenv('APPLY_YAML_DATA',
'''
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: istio-gateways-role
  namespace: {namespace}
rules:
- apiGroups:
  - networking.istio.io
  resources:
  - gateways
  verbs:
  - get
  - list
  - create
  - update
  - delete
  - patch
  - watch
''')
# Configs can be set in Configuration class directly or using helper utility
config.load_incluster_config()

v1 = client.CoreV1Api()

while True:
    try:
        w = watch.Watch()
        for event in w.stream(v1.list_namespace, _request_timeout=60):
            if event['type'] == "MODIFIED":
                print("Event: %s %s" % (event['type'], event['object'].metadata.name))
                tmp_data = APPLY_YAML_DATA.replace('{namespace}', event['object'].metadata.name)
                with tempfile.NamedTemporaryFile(dir='/tmp') as tmpfile:
                    tmp_file = tmpfile.name
                    tmpfile.close()
                print(tmp_file)
                f = open(tmp_file, "a")
                f.write(tmp_data)
                f.close()
                clientapi = client.ApiClient()
                create_from_yaml(clientapi, tmp_file, namespace=event['object'].metadata.name)
                os.remove(tmp_file)
    except Exception as e:
        print(e)
