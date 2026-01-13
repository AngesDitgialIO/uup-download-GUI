import requests
from bs4 import BeautifulSoup

# 获取首页并分析最新构建
def analyze_latest_builds():
    url = 'https://uupdump.net'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print('解析首页最新构建...')
    
    # 查找所有的构建列表
    build_lists = soup.find_all('div', class_='ui relaxed divided list')
    
    if not build_lists:
        print('未找到构建列表')
        print('页面内容预览:')
        print(response.text[:1000])
        return
    
    print(f'找到 {len(build_lists)} 个构建列表')
    
    # 分析第一个构建列表
    first_list = build_lists[0]
    build_items = first_list.find_all('div', class_='item')
    
    print(f'第一个列表包含 {len(build_items)} 个构建项目')
    
    if build_items:
        # 分析第一个构建项目
        first_item = build_items[0]
        print('\n第一个构建项目:')
        print(first_item.prettify())
        
        # 查找链接
        links = first_item.find_all('a')
        print(f'\n找到 {len(links)} 个链接:')
        for link in links:
            print(f'文本: {link.text.strip()}')
            print(f'URL: {link.get("href")}')
            
            # 如果找到构建详情链接，进一步分析
            if link.get('href') and 'id=' in link.get('href'):
                build_url = f"https://uupdump.net{link.get('href')}"
                print(f'\n分析构建详情页面: {build_url}')
                analyze_build_detail(build_url)
                return

# 分析构建详情页面
def analyze_build_detail(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print('构建详情页面分析:')
    
    # 查找下载按钮
    download_buttons = soup.find_all('a', class_='ui primary button')
    print(f'找到 {len(download_buttons)} 个主要按钮:')
    
    for button in download_buttons:
        print(f'按钮文本: {button.text.strip()}')
        print(f'按钮链接: {button.get("href")}')
        
        # 如果是下载按钮，进一步分析
        if 'download' in button.text.lower() or 'editions' in button.get('href'):
            editions_url = f"https://uupdump.net{button.get('href')}"
            print(f'\n分析版本选择页面: {editions_url}')
            analyze_editions_page(editions_url)
            return

# 分析版本选择页面
def analyze_editions_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print('版本选择页面分析:')
    
    # 查找表单和提交按钮
    forms = soup.find_all('form')
    print(f'找到 {len(forms)} 个表单:')
    
    for form in forms:
        print(f'表单动作: {form.get("action")}')
        print(f'表单方法: {form.get("method")}')
        
        # 查找隐藏字段
        hidden_fields = form.find_all('input', type='hidden')
        print(f'隐藏字段: {[(f.get("name"), f.get("value")) for f in hidden_fields]}')
        
        # 查找提交按钮
        submit_buttons = form.find_all('button', type='submit')
        print(f'提交按钮: {[b.text.strip() for b in submit_buttons]}')

if __name__ == '__main__':
    analyze_latest_builds()
