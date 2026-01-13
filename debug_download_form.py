#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试下载表单查找问题的脚本
"""

import requests
from bs4 import BeautifulSoup

def debug_download_form():
    """调试下载表单查找问题"""
    
    print("开始调试下载表单查找问题...")
    
    # 使用测试数据
    # 注意：这些数据可能需要根据实际情况进行调整
    lang_form_data = {
        "id": "7ef0fa08-2acc-43c0-9bae-3d182e99930b",  # 测试构建ID
        "pack": "zh-cn",  # 中文包
        "language": "Chinese (Simplified)"  # 中文语言
    }
    
    versions_url = "https://uupdump.net/get.php"
    print(f"提交语言选择表单到: {versions_url}")
    print(f"表单数据: {lang_form_data}")
    
    try:
        # 提交语言选择表单，获取SKU页面
        response = requests.post(versions_url, data=lang_form_data)
        response.raise_for_status()
        
        print(f"响应状态码: {response.status_code}")
        
        # 保存页面内容以便分析
        with open("sku_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print("SKU页面已保存到 sku_page.html")
        
        # 解析页面内容
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找所有表单
        all_forms = soup.find_all("form")
        print(f"页面中共有 {len(all_forms)} 个表单")
        
        if not all_forms:
            print("未找到任何表单")
            return
        
        # 打印每个表单的详细信息
        for i, form in enumerate(all_forms):
            print(f"\n表单 {i+1}:")
            print(f"  action: {form.get('action', '无')}")
            print(f"  method: {form.get('method', '无')}")
            
            # 查找表单中的所有输入字段
            input_fields = form.find_all("input")
            print(f"  输入字段数量: {len(input_fields)}")
            
            # 打印部分输入字段的信息
            for j, input_field in enumerate(input_fields[:10]):  # 只打印前10个
                name = input_field.get("name", "无名称")
                value = input_field.get("value", "无值")
                type = input_field.get("type", "无类型")
                print(f"    字段 {j+1}: type='{type}', name='{name}', value='{value}'")
        
        # 尝试查找带有download.php的表单
        print("\n尝试查找带有download.php的表单...")
        
        # 方法1: 精确匹配action="/download.php"
        download_form1 = soup.find("form", action="/download.php")
        if download_form1:
            print("方法1成功: 找到 action='/download.php' 的表单")
        else:
            print("方法1失败: 未找到 action='/download.php' 的表单")
        
        # 方法2: 模糊匹配包含download.php的action
        download_form2 = soup.find("form", action=lambda action: action and "download.php" in action)
        if download_form2:
            print(f"方法2成功: 找到包含download.php的表单，action='{download_form2.get('action')}'")
        else:
            print("方法2失败: 未找到包含download.php的表单")
        
        # 方法3: 查找所有可能的下载表单
        print("\n尝试查找所有可能的下载表单...")
        for i, form in enumerate(all_forms):
            action = form.get('action', '')
            if "download" in action.lower() or "get" in action.lower():
                print(f"找到可能的下载表单 {i+1}: action='{action}'")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_download_form()