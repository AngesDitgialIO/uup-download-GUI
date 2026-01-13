import requests
from bs4 import BeautifulSoup

# 测试数据
build_id = "bd0aacd8-17fb-4079-8cec-064fa3ffa643"
pack_value = "zh-cn"
sku_value = "CORE"  # 只选择一个SKU进行测试

# 测试不同的下载选项
print("测试不同的下载选项...")

download_options = [
    ("1", "下载 UUP 文件集"),
    ("2", "下载并转换为 ISO 镜像文件"),
    ("3", "下载、添加虚拟升级版本并转换为 ISO 镜像文件")
]

for download_value, download_name in download_options:
    print(f"\n\n=== 测试选项 {download_name} (值: {download_value}) ===")
    
    # 构建下载URL
    download_params = {
        "id": build_id,
        "pack": pack_value,
        "edition": sku_value,
        "download": download_value
    }
    
    print(f"URL参数: {download_params}")
    
    # 发送GET请求
    download_url = "https://uupdump.net/download.php"
    response = requests.get(download_url, params=download_params)
    
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"响应URL: {response.url}")
        continue
    
    print(f"请求成功，状态码: {response.status_code}")
    print(f"响应URL: {response.url}")
    
    # 查找虚拟升级版本相关内容
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找所有输入字段
    inputs = soup.find_all("input")
    print(f"\n找到 {len(inputs)} 个输入字段")
    
    for input_field in inputs:
        name = input_field.get("name")
        value = input_field.get("value")
        input_type = input_field.get("type")
        
        if name:
            print(f"  - {name} ({input_type}) = {value}")
    
    # 查找所有下拉菜单
    selects = soup.find_all("select")
    print(f"\n找到 {len(selects)} 个下拉菜单")
    
    for select in selects:
        name = select.get("name")
        print(f"  - {name}:")
        
        options = select.find_all("option")
        for option in options:
            option_value = option.get("value")
            option_text = option.text.strip()
            print(f"    - {option_value}: {option_text}")
    
    # 查找所有与虚拟或升级相关的文本
    virtual_text = soup.find_all(
        string=lambda text: text and ("虚拟" in text or "升级" in text or "virtual" in text.lower() or "upgrade" in text.lower())
    )
    
    if virtual_text:
        print(f"\n找到与虚拟升级相关的文本:")
        for text in virtual_text:
            if text.strip():
                print(f"  - {text.strip()}")
    else:
        print(f"\n未找到与虚拟升级相关的文本")
    
    # 查找下载链接
    download_links = soup.find_all("a", href=lambda href: href and "download.php" in href)
    if download_links:
        print(f"\n找到下载链接:")
        for link in download_links:
            print(f"  - {link.text.strip()}: {link.get('href')}")
    else:
        print(f"\n未找到下载链接")
