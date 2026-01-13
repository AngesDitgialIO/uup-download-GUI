import requests
from bs4 import BeautifulSoup

# 获取下载页面
def analyze_download_page():
    url = 'https://uupdump.net/known.php'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有的构建卡片
    build_cards = soup.find_all('div', class_='ui segment')
    print(f'找到 {len(build_cards)} 个构建卡片')
    
    if build_cards:
        # 分析第一个卡片
        first_card = build_cards[0]
        print('\n第一个构建卡片的结构:')
        print(first_card.prettify()[:1000])
        
        # 查找链接
        links = first_card.find_all('a')
        print(f'\n卡片内找到 {len(links)} 个链接:')
        for link in links:
            print(f'文本: {link.text.strip()}')
            print(f'URL: {link.get("href")}')

# 分析首页
def analyze_home_page():
    url = 'https://uupdump.net'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print('首页主要内容:')
    main_content = soup.find('div', class_='ui container main-content')
    if main_content:
        print(main_content.prettify()[:1000])

if __name__ == '__main__':
    print('分析uupdump.net的首页...')
    analyze_home_page()
    
    print('\n\n分析uupdump.net的下载页面...')
    analyze_download_page()
