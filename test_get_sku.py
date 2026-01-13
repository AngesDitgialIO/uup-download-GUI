import requests
from bs4 import BeautifulSoup

# 测试数据
build_id = "bd0aacd8-17fb-4079-8cec-064fa3ffa643"
pack_value = "zh-cn"

# 构建URL参数
params = {
    "id": build_id,
    "pack": pack_value
}

# 构建完整URL
url = "https://uupdump.net/selectedition.php"

print(f"测试 URL: {url}")
print(f"参数: {params}")

# 发送GET请求
response = requests.get(url, params=params)

print(f"\n响应状态码: {response.status_code}")
print(f"响应URL: {response.url}")

# 检查页面内容
if response.status_code == 200:
    # 查找SKU相关内容
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找所有表单
    forms = soup.find_all("form")
    print(f"\n找到 {len(forms)} 个表单")
    
    for i, form in enumerate(forms):
        action = form.get("action")
        method = form.get("method", "GET").upper()
        
        print(f"\n表单 {i+1}:")
        print(f"  动作: {action}")
        print(f"  方法: {method}")
        
        # 查找复选框
        checkboxes = form.find_all("input", type="checkbox")
        print(f"  复选框数量: {len(checkboxes)}")
        
        if checkboxes:
            print("  复选框:")
            for checkbox in checkboxes[:5]:  # 只显示前5个
                name = checkbox.get("name")
                value = checkbox.get("value")
                label = checkbox.find_next("label")
                if label:
                    label_text = label.text.strip()
                else:
                    label_text = "无标签"
                
                if name:
                    print(f"    - {name} = {value} : {label_text}")
    
    # 查找所有输入字段
    all_inputs = soup.find_all("input")
    print(f"\n找到 {len(all_inputs)} 个输入字段")
    
    # 查找所有按钮
    buttons = soup.find_all("button") + soup.find_all("input", type="submit")
    print(f"找到 {len(buttons)} 个按钮")
    
    for button in buttons:
        if button.name == "button":
            button_text = button.text.strip()
            button_type = button.get("type", "button")
        else:
            button_text = button.get("value", "")
            button_type = button.get("type")
        
        print(f"  - 类型: {button_type}, 文本: {button_text}")
else:
    print(f"\n请求失败，状态码: {response.status_code}")
    print(f"响应内容: {response.text[:1000]}")
