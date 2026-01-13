#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试uupdump.net的download.php请求的脚本
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_download_php():
    """调试download.php请求"""
    
    print("开始调试download.php请求...")
    
    # 使用测试数据
    form_data = {
        "id": "7efb0fa8-2acc-43c0-9bae-3d182e99930b",
        "pack": "zh-cn",
        "edition[]": ["Professional"],
        "download": "2",
        "includeUpdates": "1",
        "componentCleanup": "0",
        "netFx3": "0",
        "esdCompression": "0"
    }
    
    download_url = "https://uupdump.net/download.php"
    print(f"提交表单到: {download_url}")
    print(f"表单数据: {form_data}")
    
    try:
        # 发送POST请求
        response = requests.post(download_url, data=form_data)
        response.raise_for_status()
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应URL: {response.url}")
        
        # 检查响应是否是重定向
        if response.history:
            print("\n响应是重定向:")
            for i, hist in enumerate(response.history):
                print(f"  {i+1}. {hist.status_code} -> {hist.url}")
            print(f"  最终URL: {response.url}")
        
        # 检查Content-Type
        content_type = response.headers.get("content-type", "")
        print(f"\nContent-Type: {content_type}")
        
        # 如果是HTML，解析并查找信息
        if "text/html" in content_type:
            print("\n响应是HTML页面")
            
            # 保存页面内容
            with open("download_php_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            print("页面已保存到 download_php_response.html")
            
            # 解析页面
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 查找所有表单
            forms = soup.find_all("form")
            print(f"\n页面中共有 {len(forms)} 个表单")
            for i, form in enumerate(forms):
                action = form.get("action", "无")
                method = form.get("method", "无")
                print(f"表单 {i+1}: action='{action}', method='{method}'")
                
                # 查找表单中的隐藏字段
                hidden_fields = form.find_all("input", type="hidden")
                if hidden_fields:
                    print("  隐藏字段:")
                    for field in hidden_fields:
                        name = field.get("name", "无名称")
                        value = field.get("value", "无值")
                        print(f"    {name} = {value}")
            
            # 查找所有JavaScript
            scripts = soup.find_all("script")
            print(f"\n页面中共有 {len(scripts)} 个JavaScript标签")
            
            # 检查JavaScript中是否有重定向或下载链接
            for i, script in enumerate(scripts):
                script_content = script.string
                if script_content:
                    # 查找window.location或location.href
                    if "window.location" in script_content or "location.href" in script_content:
                        print(f"\n脚本 {i+1} 包含重定向:")
                        print(script_content[:200] + "...")
                    
                    # 查找下载链接
                    if ".zip" in script_content:
                        print(f"\n脚本 {i+1} 包含ZIP链接:")
                        print(script_content[:200] + "...")
            
            # 查找所有按钮
            buttons = soup.find_all("button")
            print(f"\n页面中共有 {len(buttons)} 个按钮")
            for i, button in enumerate(buttons[:5]):  # 只显示前5个
                text = button.text.strip()
                onclick = button.get("onclick", "")
                print(f"按钮 {i+1}: {text}")
                if onclick:
                    print(f"  onclick: {onclick}")
            
            # 查找所有链接
            links = soup.find_all("a", href=True)
            print(f"\n页面中共有 {len(links)} 个链接")
            
            # 查找ZIP链接
            zip_links = [link for link in links if link.get("href", "").lower().endswith(".zip")]
            if zip_links:
                print(f"\n找到 {len(zip_links)} 个ZIP链接:")
                for i, link in enumerate(zip_links):
                    href = link.get("href")
                    text = link.text.strip()
                    print(f"  {i+1}. {href} - {text}")
            
            # 查找包含download的链接
            download_links = [link for link in links if "download" in link.get("href", "").lower()]
            if download_links:
                print(f"\n找到 {len(download_links)} 个包含download的链接:")
                for i, link in enumerate(download_links[:5]):  # 只显示前5个
                    href = link.get("href")
                    text = link.text.strip()
                    print(f"  {i+1}. {href} - {text}")
        
        # 如果是二进制文件，保存前100字节
        else:
            print("\n响应是二进制文件")
            
            # 保存前100字节
            first_bytes = response.content[:100]
            print(f"\n前100字节: {first_bytes!r}")
            
            # 检查是否是ZIP文件
            if first_bytes.startswith(b"PK"):
                print("文件是ZIP文件")
            else:
                print("文件不是ZIP文件")
        
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_download_php()