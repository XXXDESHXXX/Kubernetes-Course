import kopf
import kubernetes
from kubernetes.client.rest import ApiException

kubernetes.config.load_kube_config()

@kopf.on.create('example.com', 'v1', 'databases')
def create_database(spec, name, namespace, **kwargs):
    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {'app': 'database'}
        },
        'spec': {
            'containers': [{
                'name': 'database-container',
                'image': 'nginx',
                'ports': [{'containerPort': 80}],
            }]
        }
    }
    api = kubernetes.client.CoreV1Api()
    try:
        api.create_namespaced_pod(namespace=namespace, body=pod_manifest)
        kopf.info(body=pod_manifest, reason="PodCreated", message=f"Pod {name} создан для объекта Database {name}.")
    except ApiException as e:
        raise kopf.TemporaryError(f"Ошибка при создании pod: {e}", delay=30)

@kopf.on.delete('example.com', 'v1', 'databases')
def delete_database(name, namespace, **kwargs):
    api = kubernetes.client.CoreV1Api()
    try:
        api.delete_namespaced_pod(name=name, namespace=namespace)
        kopf.info(message=f"Pod {name} удалён после удаления объекта Database.", reason="PodDeleted")
    except ApiException as e:
        kopf.logger.error(f"Ошибка при удалении pod {name}: {e}")
