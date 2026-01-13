import requests
from bs4 import BeautifulSoup

# 使用示例构建ID（从程序中复制）
build_id = "bd0aacd8-17fb-4079-8cec-064fa3ffa643"
build_name = "Windows 11 Insider Preview Feature Update (26220.7535) arm64"

# 构建URL
build_url = f"https://uupdump.net/selectlang.php?id={build_id}"

print(f"测试构建: {build_name}")
print(f"构建ID: {build_id}")
print(f"URL: {build_url}")
print()

# 发送请求
print("正在发送请求...")
try:
    response = requests.get(build_url)
    response.raise_for_status()
    
    print(f"请求成功，状态码: {response.status_code}")
    print(f"页面长度: {len(response.text)} 字符")
    print()
    
    # 检查页面是否包含错误信息
    if "Error" in response.text or "error" in response.text:
        print("警告: 页面包含错误信息!")
    
    # 检查页面是否包含语言选项
    if "选择语言" in response.text or "Select language" in response.text:
        print("找到语言选择相关内容!")
    else:
        print("未找到语言选择相关内容!")
    
    # 解析HTML
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找所有表单
    forms = soup.find_all("form")
    print(f"\n找到 {len(forms)} 个表单")
    
    for i, form in enumerate(forms):
        action = form.get("action")
        print(f"\n表单 {i+1}:")
        print(f"  动作: {action}")
        
        # 查找输入字段
        inputs = form.find_all("input")
        print(f"  输入字段数量: {len(inputs)}")
        
        for input_field in inputs[:5]:  # 只显示前5个
            name = input_field.get("name")
            value = input_field.get("value")
            input_type = input_field.get("type")
            print(f"    - {name} ({input_type}): {value}")
    
    # 查找所有链接
    links = soup.find_all("a")
    print(f"\n找到 {len(links)} 个链接")
    
    # 查找包含download.php的链接
    download_links = [link for link in links if link.get("href") and "download.php" in link.get("href")]
    print(f"找到 {len(download_links)} 个下载链接")
    
    for link in download_links:
        print(f"  - {link.get('href')} - {link.text.strip()}")
    
    # 保存页面内容到文件以便查看
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"\n页面内容已保存到 debug_page.html")
    
    # 检查是否重定向
    print(f"\n请求历史:")
    for i, hist in enumerate(response.history):
        print(f"  重定向 {i+1}: {hist.status_code} -> {hist.url}")
    
    print(f"  最终URL: {response.url}")
    
    # 检查响应头
    print(f"\n响应头: {dict(response.headers)[:3]}")  # 只显示前3个
    
    
except requests.exceptions.RequestException as e:
    print(f"请求失败: {str(e)}")
    import traceback
    traceback.print_exc()
