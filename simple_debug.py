#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的UUP下载链接调试脚本
"""

import requests
from bs4 import BeautifulSoup

def debug_uupdump_links():
    """调试uupdump.net的下载链接"""
    
    print("开始调试uupdump.net的下载链接...")
    
    # 直接访问uupdump.net主页
    try:
        url = "https://uupdump.net"
        response = requests.get(url)
        response.raise_for_status()
        
        print(f"访问主页成功，状态码: {response.status_code}")
        
        # 解析主页
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找最新的构建链接
        builds = []
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            if "/selectlang.php?id=" in href:
                build_id = href.split("id=")[1]
                build_name = link.text.strip()
                builds.append((build_name, build_id))
        
        if not builds:
            print("未找到任何构建链接")
            return
            
        print(f"找到 {len(builds)} 个构建")
        print(f"第一个构建: {builds[0][0]} (ID: {builds[0][1]})")
        
        # 访问构建页面
        build_name, build_id = builds[0]
        build_url = f"https://uupdump.net/selectlang.php?id={build_id}"
        
        print(f"\n访问构建页面: {build_url}")
        response = requests.get(build_url)
        response.raise_for_status()
        
        # 解析构建页面
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 查找语言选择表单
        lang_form = soup.find("form")
        if lang_form:
            action = lang_form.get("action", "无")
            method = lang_form.get("method", "无")
            print(f"找到语言选择表单: action='{action}', method='{method}'")
        
        # 查找语言选项
        select_element = soup.find("select")
        if select_element:
            select_name = select_element.get("name", "无名称")
            options = select_element.find_all("option")
            print(f"找到语言选择下拉菜单: name='{select_name}', {len(options)} 个选项")
            
            # 获取第一个语言选项
            if len(options) > 1:
                first_option = options[1]  # 跳过第一个空选项
                option_value = first_option.get("value")
                option_text = first_option.text.strip()
                print(f"第一个语言选项: {option_text} (值: {option_value})")
        
        # 查找隐藏字段
        hidden_fields = soup.find_all("input", type="hidden")
        print(f"\n找到 {len(hidden_fields)} 个隐藏字段")
        for field in hidden_fields:
            name = field.get("name", "无名称")
            value = field.get("value", "无值")
            print(f"隐藏字段: name='{name}', value='{value}'")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_uupdump_links()