import requests
from bs4 import BeautifulSoup

# 检查首页的构建ID格式
def check_build_ids():
    url = 'https://uupdump.net'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有包含id参数的链接
    links = soup.find_all('a', href=lambda href: href and 'id=' in href)
    
    print(f'找到 {len(links)} 个包含id参数的链接')
    
    for i, link in enumerate(links[:5]):
        href = link.get('href')
        text = link.text.strip()
        print(f'链接 {i+1}:')
        print(f'  完整URL: {href}')
        print(f'  文本内容: {text}')
        
        # 提取构建ID
        if 'id=' in href:
            build_id = href.split('id=')[-1]
            print(f'  提取的构建ID: {build_id}')
        
        print()

if __name__ == '__main__':
    check_build_ids()
