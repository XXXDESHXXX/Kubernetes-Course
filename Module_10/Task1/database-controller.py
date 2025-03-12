import time
from kubernetes import client, config, watch

config.load_kube_config()

crd_api = client.CustomObjectsApi()
namespace = "default"

w = watch.Watch()
for event in w.stream(crd_api.list_namespaced_custom_object,
                      group="example.com",
                      version="v1alpha1",
                      namespace=namespace,
                      plural="databases"):
    db_obj = event["object"]
    name = db_obj["metadata"]["name"]
    current_phase = db_obj.get("status", {}).get("phase", "Creating")
    print(f"Обнаружен объект {name} с phase={current_phase}")
    if current_phase != "Running":
        time.sleep(10)
        body = {"status": {"phase": "Running"}}
        try:
            crd_api.patch_namespaced_custom_object_status(
                group="example.com",
                version="v1alpha1",
                namespace=namespace,
                plural="databases",
                name=name,
                body=body
            )
            print(f"Обновлен статус {name} -> Running")
        except Exception as e:
            print(f"Ошибка обновления статуса для {name}: {e}")
