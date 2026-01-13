#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试虚拟升级版本功能的脚本
"""

import requests
from bs4 import BeautifulSoup

def test_virtual_upgrade():
    """测试虚拟升级版本功能"""
    
    print("开始测试虚拟升级版本功能...")
    
    # 1. 获取最新构建
    try:
        url = "https://uupdump.net"
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找构建项目
        builds = []
        
        # 查找所有包含id参数的链接
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            if "/selectlang.php?id=" in href:
                # 提取构建ID
                build_id = href.split("id=")[1]
                
                # 获取构建名称
                build_name = link.text.strip()
                if build_name and build_id:
                    builds.append((build_name, build_id))
        
        # 如果没有找到，尝试另一种方法：查找所有带有data-id属性的元素
        if not builds:
            for div in soup.find_all("div", attrs={"data-id": True}):
                build_id = div.get("data-id")
                
                # 查找构建名称
                name_span = div.find("span", class_="name")
                if name_span:
                    build_name = name_span.text.strip()
                    builds.append((build_name, build_id))
        
        # 如果仍然没有找到，尝试查找包含GUID的链接
        if not builds:
            import re
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                # 使用正则表达式匹配GUID格式
                match = re.search(r'id=([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', href)
                if match:
                    build_id = match.group(1)
                    build_name = link.text.strip() or f"构建 {build_id[:8]}"
                    builds.append((build_name, build_id))
        
        if not builds:
            print("未找到任何构建")
            return
            
        print(f"找到 {len(builds)} 个构建")
        print(f"第一个构建: {builds[0][0]} (ID: {builds[0][1]})")
        
    except Exception as e:
        print(f"获取最新构建失败: {str(e)}")
        return
    
    # 2. 获取语言选择表单
    try:
        build_name, build_id = builds[0]
        lang_url = f"https://uupdump.net/selectlang.php?id={build_id}"
        
        print(f"获取语言选择表单: {lang_url}")
        response = requests.get(lang_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找语言选择表单
        lang_form = soup.find("form", action="/get.php")
        if not lang_form:
            print("未找到语言选择表单")
            return
            
        # 查找语言选项
        lang_select = lang_form.find("select", id="language")
        if not lang_select:
            print("未找到语言选择下拉菜单")
            return
            
        # 提取语言选项
        lang_options = []
        for option in lang_select.find_all("option"):
            value = option.get("value")
            text = option.text.strip()
            if value:
                lang_options.append((text, value))
        
        if not lang_options:
            print("未找到任何语言选项")
            return
            
        print(f"找到 {len(lang_options)} 种语言选项")
        print(f"第一种语言: {lang_options[0][0]} (值: {lang_options[0][1]})")
        
    except Exception as e:
        print(f"获取语言选择表单失败: {str(e)}")
        return
    
    # 3. 提交语言选择，获取SKU页面
    try:
        # 使用第一个语言选项
        lang_name, lang_value = lang_options[0]
        
        form_data = {
            "id": build_id,
            "language": lang_value
        }
        
        versions_url = "https://uupdump.net/get.php"
        print(f"提交语言选择，获取SKU页面")
        
        response = requests.get(versions_url, params=form_data)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找SKU复选框
        sku_checkboxes = soup.find_all(
            "input",
            attrs={
                "type": "checkbox",
                "name": "edition[]"
            }
        )
        
        if not sku_checkboxes:
            print("未找到SKU复选框")
            return
            
        print(f"找到 {len(sku_checkboxes)} 个SKU版本")
        
        skus = []
        for checkbox in sku_checkboxes:
            sku_value = checkbox.get("value")
            sku_label = checkbox.find_next("label")
            
            if sku_value and sku_label:
                sku_name = sku_label.text.strip()
                skus.append((sku_name, sku_value))
        
        if not skus:
            print("未提取到任何SKU版本")
            return
            
        print(f"提取到 {len(skus)} 个SKU版本")
        print(f"第一个SKU版本: {skus[0][0]} (值: {skus[0][1]})")
        
    except Exception as e:
        print(f"获取SKU页面失败: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return
    
    # 4. 测试虚拟升级版本
    try:
        # 使用第一个SKU
        sku_name, sku_value = skus[0]
        
        # 构建下载页面URL参数
        params = {
            "id": build_id,
            "pack": "zh-cn",  # 使用中文包作为示例
            "edition": sku_value,
            "download": "3"  # 使用第三种下载方式来获取虚拟升级版本
        }
        
        download_url = "https://uupdump.net/download.php"
        print(f"访问下载页面获取虚拟升级版本，参数: {params}")
        
        response = requests.get(download_url, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找虚拟升级版本复选框
        virtual_checkboxes = soup.find_all(
            "input",
            attrs={
                "type": "checkbox",
                "name": "virtualEditions[]"
            }
        )
        
        print(f"找到 {len(virtual_checkboxes)} 个虚拟升级版本")
        
        if not virtual_checkboxes:
            print("未找到任何虚拟升级版本")
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
        
    except Exception as e:
        print(f"测试虚拟升级版本失败: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return

if __name__ == "__main__":
    test_virtual_upgrade()