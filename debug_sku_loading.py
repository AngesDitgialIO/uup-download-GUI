import requests
from bs4 import BeautifulSoup

# 测试SKU加载功能
def debug_sku_loading():
    # 使用示例构建ID
    build_id = "bd0aacd8-17fb-4079-8cec-064fa3ffa643"
    
    # 1. 首先访问语言选择页面
    lang_url = f"https://uupdump.net/selectlang.php?id={build_id}"
    print(f"访问语言选择页面: {lang_url}")
    
    response = requests.get(lang_url)
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 2. 查找语言选择表单
    lang_form = soup.find("form", action="selectedition.php")
    if not lang_form:
        print("未找到语言选择表单")
        return
    
    # 3. 构建语言选择表单数据
    select_element = lang_form.find("select")
    if not select_element:
        print("未找到语言选择下拉菜单")
        return
    
    # 选择中文(简体)
    select_name = select_element.get("name")
    
    # 查找中文选项
    chinese_option = select_element.find("option", text=lambda text: text and "Chinese (Simplified)" in text)
    if not chinese_option:
        print("未找到中文(简体)选项")
        # 打印所有选项
        print("所有可用语言选项:")
        for option in select_element.find_all("option"):
            print(f"  - {option.text.strip()}")
        return
    
    chinese_value = chinese_option.get("value")
    print(f"选择中文(简体)，值为: {chinese_value}")
    
    # 4. 构建完整的表单数据
    form_data = {}
    
    # 添加隐藏字段
    hidden_fields = lang_form.find_all("input", type="hidden")
    for field in hidden_fields:
        name = field.get("name")
        value = field.get("value")
        if name and value:
            form_data[name] = value
    
    # 添加语言选择
    form_data[select_name] = chinese_value
    
    print(f"表单数据: {form_data}")
    
    # 5. 提交语言选择表单
    print("\n提交语言选择表单...")
    edition_url = "https://uupdump.net/selectedition.php"
    response = requests.post(edition_url, data=form_data)
    
    if response.status_code != 200:
        print(f"提交失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}...")
        return
    
    print(f"提交成功，响应状态码: {response.status_code}")
    
    # 6. 保存页面内容以便分析
    with open("sku_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print("页面内容已保存到 sku_page.html")
    
    # 7. 分析SKU选项
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找所有SKU复选框
    print("\n查找SKU复选框...")
    sku_checkboxes = soup.find_all(
        "input",
        attrs={
            "type": "checkbox",
            "name": lambda name: name and name.startswith("sku_")
        }
    )
    
    print(f"找到 {len(sku_checkboxes)} 个SKU复选框")
    
    if sku_checkboxes:
        for i, checkbox in enumerate(sku_checkboxes):
            sku_id = checkbox.get("name")
            sku_name = checkbox.find_next("label").text.strip() if checkbox.find_next("label") else "未知"
            print(f"SKU {i+1}: {sku_id} - {sku_name}")
    else:
        # 如果没有找到，尝试查找其他可能的SKU选择方式
        print("\n尝试其他方式查找SKU:")
        
        # 查找所有复选框
        all_checkboxes = soup.find_all("input", type="checkbox")
        print(f"找到 {len(all_checkboxes)} 个复选框")
        for checkbox in all_checkboxes[:10]:  # 只显示前10个
            name = checkbox.get("name")
            value = checkbox.get("value")
            label = checkbox.find_next("label").text.strip() if checkbox.find_next("label") else "无标签"
            print(f"  - {name}: {value} - {label}")
        
        # 查找包含SKU的div
        sku_divs = soup.find_all("div", class_=lambda cls: cls and "sku" in cls.lower())
        print(f"\n找到 {len(sku_divs)} 个包含SKU的div")
        for div in sku_divs[:5]:
            print(f"  - {div.text.strip()[:100]}...")

if __name__ == "__main__":
    debug_sku_loading()
