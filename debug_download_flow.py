#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试完整的UUP下载流程
"""

import requests
from bs4 import BeautifulSoup

def debug_download_flow():
    """调试完整的下载流程"""
    print("开始调试完整的下载流程...")
    
    # 步骤1: 模拟选择语言和SKU
    lang_form_data = {
        "id": "7efb0fa8-2acc-43c0-9bae-3d182e99930b",
        "pack": "zh-cn"
    }
    
    selected_sku_values = ["PROFESSIONAL"]
    
    print(f"\n步骤1: 选择语言和SKU")
    print(f"语言表单数据: {lang_form_data}")
    print(f"选择的SKU: {selected_sku_values}")
    
    # 步骤2: 获取SKU页面
    versions_url = "https://uupdump.net/selectedition.php"
    print(f"\n步骤2: 获取SKU页面")
    print(f"URL: {versions_url}")
    print(f"参数: {lang_form_data}")
    
    try:
        response = requests.get(versions_url, params=lang_form_data)
        response.raise_for_status()
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应URL: {response.url}")
        
        # 保存SKU页面
        with open("debug_sku_page_full.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # 步骤3: 查找下载表单
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 尝试多种方式查找下载表单
        download_form = soup.find("form", action="/download.php")
        
        if not download_form:
            # 尝试模糊匹配包含download.php的action
            download_form = soup.find("form", action=lambda action: action and "download.php" in action)
        
        if not download_form:
            # 尝试查找带有method="post"的表单
            download_form = soup.find("form", method="post")
        
        if not download_form:
            print("未找到下载表单")
            return
        
        print(f"\n步骤3: 找到下载表单")
        print(f"表单Action: {download_form.get('action')}")
        print(f"表单Method: {download_form.get('method')}")
        
        # 步骤4: 构建下载表单数据
        form_data = {}
        
        # 首先添加lang_form_data中的所有数据
        form_data.update(lang_form_data)
        print(f"\n添加lang_form_data: {lang_form_data}")
        
        # 添加表单中的输入字段
        for input_field in download_form.find_all("input"):
            name = input_field.get("name")
            value = input_field.get("value")
            type_attr = input_field.get("type")
            
            print(f"找到输入字段: name='{name}', value='{value}', type='{type_attr}'")
            
            # 特殊处理edition字段
            if name == "edition" and not value:
                print(f"  跳过空的edition隐藏字段")
                continue
            
            if name and value:
                form_data[name] = value
                print(f"  添加到表单数据: {name}={value}")
        
        # 添加选择的SKU
        form_data["edition[]"] = selected_sku_values
        if selected_sku_values:
            form_data["edition"] = selected_sku_values[0]
        
        print(f"\n添加SKU信息:")
        print(f"  edition[]: {form_data['edition[]']}")
        print(f"  edition: {form_data['edition']}")
        
        # 添加下载选项
        form_data["download"] = "2"  # 下载并转换为ISO镜像文件
        form_data["includeUpdates"] = "1"
        form_data["componentCleanup"] = "0"
        form_data["netFx3"] = "0"
        form_data["esdCompression"] = "0"
        
        print(f"\n添加下载选项:")
        print(f"  download: {form_data['download']}")
        print(f"  includeUpdates: {form_data['includeUpdates']}")
        print(f"  componentCleanup: {form_data['componentCleanup']}")
        print(f"  netFx3: {form_data['netFx3']}")
        print(f"  esdCompression: {form_data['esdCompression']}")
        
        # 步骤5: 提交下载表单
        download_url = "https://uupdump.net/download.php"
        print(f"\n步骤5: 提交下载表单")
        print(f"URL: {download_url}")
        print(f"完整表单数据:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")
        
        # 发送POST请求
        response = requests.post(download_url, data=form_data)
        response.raise_for_status()
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应URL: {response.url}")
        
        # 保存下载页面
        with open("debug_download_page_full.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # 检查响应是否是错误页面
        if "Error" in response.text and "Update ID was not specified" in response.text:
            print("\n错误: 服务器返回'Update ID was not specified'错误")
            print("这表明id参数没有正确传递到下载页面")
            
            # 检查请求是否正确包含id参数
            if "id" in form_data:
                print(f"表单数据中包含id参数: {form_data['id']}")
            else:
                print("表单数据中不包含id参数！")
                
            # 检查响应是否是重定向
            if response.history:
                print("\n响应是重定向:")
                for i, hist in enumerate(response.history):
                    print(f"  {i+1}. {hist.status_code} -> {hist.url}")
                    # 检查重定向URL是否包含id参数
                    if "id=" in hist.url:
                        print(f"  ✓ 包含id参数")
                    else:
                        print(f"  ✗ 不包含id参数")
                print(f"  最终URL: {response.url}")
        else:
            print("\n成功: 服务器没有返回'Update ID was not specified'错误")
            
            # 查找下载链接
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            
            print(f"\n页面中共有 {len(links)} 个链接")
            print("\n可能的下载链接:")
            for i, link in enumerate(links):
                href = link.get("href")
                text = link.text.strip()
                
                if "download" in href or "uup" in href or ".zip" in href:
                    print(f"  {i+1}. {href} - {text}")
        
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_download_flow()