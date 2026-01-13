#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试UUP下载工具的SKU页面处理
"""

import requests
from bs4 import BeautifulSoup

def debug_sku_page():
    """调试SKU页面"""
    print("开始调试SKU页面...")
    
    # 测试数据
    lang_form_data = {
        "id": "7efb0fa8-2acc-43c0-9bae-3d182e99930b",
        "pack": "zh-cn"
    }
    
    versions_url = "https://uupdump.net/selectedition.php"
    print(f"提交到: {versions_url}")
    print(f"参数: {lang_form_data}")
    
    try:
        # 发送GET请求
        response = requests.get(versions_url, params=lang_form_data)
        response.raise_for_status()
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应URL: {response.url}")
        
        # 保存页面内容
        with open("debug_sku_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"\n页面已保存到 debug_sku_page.html")
        
        # 解析页面
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找所有表单
        forms = soup.find_all("form")
        print(f"\n页面中共有 {len(forms)} 个表单")
        
        for i, form in enumerate(forms):
            action = form.get("action", "无")
            method = form.get("method", "无")
            
            print(f"\n表单 {i+1}:")
            print(f"  Action: {action}")
            print(f"  Method: {method}")
            
            # 查找所有输入字段
            inputs = form.find_all("input")
            print(f"  输入字段数量: {len(inputs)}")
            
            for j, input_field in enumerate(inputs):
                name = input_field.get("name", "无名称")
                value = input_field.get("value", "无值")
                type_attr = input_field.get("type", "无类型")
                
                print(f"    字段 {j+1}: name='{name}', value='{value}', type='{type_attr}'")
            
            # 查找所有选择字段
            selects = form.find_all("select")
            for j, select in enumerate(selects):
                name = select.get("name", "无名称")
                
                print(f"    选择字段 {j+1}: name='{name}'")
                
                options = select.find_all("option")
                for k, option in enumerate(options):
                    option_value = option.get("value", "无值")
                    option_text = option.text.strip()
                    
                    print(f"      选项 {k+1}: value='{option_value}', text='{option_text}'")
            
            # 查找所有按钮
            buttons = form.find_all("button")
            for j, button in enumerate(buttons):
                button_text = button.text.strip()
                onclick = button.get("onclick", "无")
                
                print(f"    按钮 {j+1}: text='{button_text}', onclick='{onclick}'")
        
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sku_page()