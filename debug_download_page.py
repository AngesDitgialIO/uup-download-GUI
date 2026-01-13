#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试下载页面结构的脚本
"""

import requests
from bs4 import BeautifulSoup

def debug_download_page():
    """调试下载页面结构"""
    
    print("开始调试下载页面结构...")
    
    # 使用一个已知的构建ID和参数来测试
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
    print(f"提交下载表单到: {download_url}")
    
    try:
        # 提交下载表单
        response = requests.post(download_url, data=form_data)
        response.raise_for_status()
        
        print(f"响应状态码: {response.status_code}")
        
        # 保存页面内容
        with open("debug_download_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print("下载页面已保存到 debug_download_page.html")
        
        # 解析页面
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找所有按钮
        buttons = soup.find_all("button")
        print(f"\n页面中共有 {len(buttons)} 个按钮")
        for i, button in enumerate(buttons):
            text = button.text.strip()
            print(f"按钮 {i+1}: {text}")
        
        # 查找所有带有ui类的元素
        ui_elements = soup.find_all(class_=lambda cls: cls and "ui" in cls)
        print(f"\n页面中共有 {len(ui_elements)} 个UI元素")
        for i, element in enumerate(ui_elements[:10]):  # 只打印前10个
            tag = element.name
            classes = element.get("class", [])
            text = element.text.strip()
            print(f"UI元素 {i+1}: <{tag}> {classes} - {text[:50]}...")
        
        # 查找所有下载相关的链接
        download_links = soup.find_all("a", href=lambda href: href and ("download" in href.lower() or "uup" in href.lower()))
        print(f"\n页面中共有 {len(download_links)} 个下载相关链接")
        for i, link in enumerate(download_links):
            href = link.get("href")
            text = link.text.strip()
            classes = link.get("class", [])
            print(f"链接 {i+1}: {href} - {text} - 类: {classes}")
        
        # 查找所有带有href的链接（更广泛的搜索）
        all_links = soup.find_all("a", href=True)
        print(f"\n页面中共有 {len(all_links)} 个链接")
        
        # 查找可能的下载链接（不包含git、faq等）
        possible_download_links = []
        for link in all_links:
            href = link.get("href")
            if href and "download" in href.lower() and "git" not in href.lower() and "faq" not in href.lower() and not href.lower().endswith(".md"):
                possible_download_links.append(link)
        
        print(f"\n可能的下载链接: {len(possible_download_links)}")
        for i, link in enumerate(possible_download_links):
            href = link.get("href")
            text = link.text.strip()
            classes = link.get("class", [])
            print(f"可能的下载链接 {i+1}: {href} - {text} - 类: {classes}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_download_page()