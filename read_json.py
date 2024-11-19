import json

with open("config.json", "r", encoding="utf-8") as json_data:
    data = json.load(json_data)

for group in data:
    print(f"Group ID: {group['group_id']}")
    for device in group['device']:
        print(f"  Hostname: {device['hostname']}")
        print(f"  Cameras: {device['cameras']}")
        print(f"  IP: {device['ip']}")
        print(f"  RTSP: {device['rtsp']}")
        print()
