from bs4 import BeautifulSoup

# 读取保存的页面内容
with open('debug_page.html', 'r', encoding='utf-8') as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

print("分析语言选择页面结构...")
print()

# 查找所有卡片式元素
cards = []

# 尝试不同的卡片类名
card_classes = ['ui card', 'ui segment', 'language-card']

for card_class in card_classes:
    found_cards = soup.find_all('div', class_=card_class.split())
    if found_cards:
        cards.extend(found_cards)

print(f"找到 {len(cards)} 个卡片式元素")

# 分析每个卡片
for i, card in enumerate(cards):
    print(f"\n--- 卡片 {i+1} ---\n")
    
    # 查找语言名称
    lang_name = "未知语言"
    
    # 尝试查找h3/h4标题
    header = card.find('h3') or card.find('h4')
    if header:
        lang_name = header.text.strip()
        print(f"语言名称 (标题): {lang_name}")
    
    # 尝试查找strong标签
    strong_tag = card.find('strong')
    if strong_tag:
        lang_name = strong_tag.text.strip()
        print(f"语言名称 (strong): {lang_name}")
    
    # 尝试查找卡片内的文本
    if not header and not strong_tag:
        card_text = card.text.strip()
        if card_text:
            lang_name = card_text.split('\n')[0].strip()
            print(f"语言名称 (文本): {lang_name}")
    
    # 查找表单
    form = card.find('form')
    if form:
        action = form.get('action')
        print(f"表单动作: {action}")
        
        # 查找表单内的输入字段
        inputs = form.find_all('input')
        print(f"输入字段数量: {len(inputs)}")
        
        form_data = {}
        for input_field in inputs:
            name = input_field.get('name')
            value = input_field.get('value')
            input_type = input_field.get('type')
            
            if name and value:
                form_data[name] = value
                print(f"  - {name} ({input_type}): {value}")
        
        print(f"表单数据: {form_data}")
    
    # 显示卡片的部分HTML
    print(f"\n卡片HTML (前500字符):")
    print(str(card)[:500])
    print("...")

# 查找所有链接
links = soup.find_all('a')
print(f"\n\n找到 {len(links)} 个链接")

# 查找包含特定关键词的链接
keywords = ['selectedition', 'get.php', 'download']
for keyword in keywords:
    matching_links = [link for link in links if link.get('href') and keyword in link.get('href')]
    print(f"\n包含 '{keyword}' 的链接 ({len(matching_links)} 个):")
    for link in matching_links[:3]:
        print(f"  - {link.get('href')} - {link.text.strip()}")
