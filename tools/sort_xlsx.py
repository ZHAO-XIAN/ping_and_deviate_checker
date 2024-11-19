import re
import json

# 读取文件
with open("output.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# 定义正则表达式，用于提取相关信息
sheet_name_pattern = re.compile(r"### 工作表名稱: (.*?) ###")
device_pattern = re.compile(r"nan (.*?) (.*?) (.*?) (.*?) (.*?) (.*?) (.*?) (.*?) (.*?) (.*?)")

# 存储所有工作表数据
sheets = {}

current_sheet = None

# 解析文件
for line in lines:
    # 查找工作表名称
    sheet_match = sheet_name_pattern.match(line)
    if sheet_match:
        sheet_name = sheet_match.group(1)
        current_sheet = sheet_name
        sheets[current_sheet] = []
        continue
    
    # 查找设备信息
    device_match = device_pattern.match(line)
    if device_match and current_sheet:
        device_info = device_match.groups()
        device_name = device_info[1]  # 获取设备名称
        external_ip = device_info[3]  # 获取外部IP
        rtsp_url = device_info[7]  # 获取RTSP地址

        # 解析端口号
        ip_port = external_ip.split(":")
        ip = ip_port[0]
        port = ip_port[1] if len(ip_port) > 1 else ""

        # 检查 ip 和 cameras 是否符合条件，符合条件才添加到列表
        if ip not in ["nan", "", "外部IP"] and device_name != "名稱" and "kr" not in device_name and "kp" not in device_name and "Switch" not in device_name and rtsp_url != "ssh":
            # 将数据添加到当前工作表
            sheets[current_sheet].append({
                "hostname": "",
                "cameras": device_name,
                "ip": ip,
                "rtsp": rtsp_url
            })

# 格式化输出为所需的 JSON 结构
output_data = []
for sheet_name, devices in sheets.items():
    group_id = sheet_name.split()[0]  # 获取 group_id（例如：台1線437K+500 -> t1436k）
    output_data.append({
        "group_id": group_id,
        "device": devices
    })

# 输出为 JSON 格式并写入文件
with open('output_dd.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

# 打印结果
print(json.dumps(output_data, ensure_ascii=False, indent=4))
