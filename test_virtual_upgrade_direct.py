#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接测试虚拟升级版本功能的脚本
"""

import requests
from bs4 import BeautifulSoup

def test_virtual_upgrade():
    """测试虚拟升级版本功能"""
    
    print("开始测试虚拟升级版本功能...")
    
    # 直接测试虚拟升级版本功能
    try:
        # 使用一个已知的构建ID和参数来测试虚拟升级版本
        # 注意：这些参数可能需要根据实际情况进行调整
        params = {
            "id": "bd0aacd8-17fb-4079-8cec-064fa3ffa643",  # 使用找到的构建ID
            "pack": "zh-cn",  # 中文包
            "edition": "professional",  # 专业版SKU
            "download": "3"  # 使用第三种下载方式来获取虚拟升级版本
        }
        
        download_url = "https://uupdump.net/download.php"
        print(f"访问下载页面获取虚拟升级版本，参数: {params}")
        
        response = requests.get(download_url, params=params)
        response.raise_for_status()
        
        # 保存页面内容以便调试
        with open("download_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找虚拟升级版本复选框
        virtual_checkboxes = soup.find_all(
            "input",
            attrs={
                "type": "checkbox",
                "name": "virtualEditions[]"
            }
        )
        
        print(f"找到 {len(virtual_checkboxes)} 个虚拟升级版本复选框")
        
        if not virtual_checkboxes:
            print("未找到任何虚拟升级版本")
            print("开始搜索页面中的所有复选框...")
            
            # 查找页面中的所有复选框
            all_checkboxes = soup.find_all("input", attrs={"type": "checkbox"})
            print(f"页面中共有 {len(all_checkboxes)} 个复选框")
            
            # 打印所有复选框的名称和值
            for checkbox in all_checkboxes[:10]:  # 只打印前10个
                name = checkbox.get("name", "无名称")
                value = checkbox.get("value", "无值")
                print(f"复选框: name='{name}', value='{value}'")
                
            return
            
        virtual_editions = []
        
        for checkbox in virtual_checkboxes:
            virtual_value = checkbox.get("value")
            virtual_label = checkbox.find_next("label")
            
            if virtual_value and virtual_label:
                virtual_name = virtual_label.text.strip()
                virtual_editions.append((virtual_name, virtual_value))
        
        if not virtual_editions:
            print("未提取到任何虚拟升级版本")
            return
            
        print(f"提取到 {len(virtual_editions)} 个虚拟升级版本")
        
        for virtual_name, virtual_value in virtual_editions:
            print(f"虚拟升级版本: {virtual_name} (值: {virtual_value})")
        
        print("虚拟升级版本功能测试成功!")
        print("\n功能总结:")
        print("1. 能够访问下载页面")
        print("2. 能够找到虚拟升级版本复选框")
        print("3. 能够提取虚拟升级版本的名称和值")
        print("4. 可以在下载表单中包含这些虚拟升级版本")
        
    except Exception as e:
        print(f"测试虚拟升级版本失败: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return

if __name__ == "__main__":
    test_virtual_upgrade()