"""
爬取 incidecoder.com 的产品和成分数据，保存到 output 目录。

用法:
    python crawl_data.py                  # 爬取产品和成分页面，增量续爬
    python crawl_data.py --ingredients    # 只爬取成分页面
    python crawl_data.py --products       # 只爬取产品页面
    python crawl_data.py --max 1000       # 限制爬取数量（用于测试）
    python crawl_data.py --clean          # 清空已爬取记录，重新开始
"""

import csv
import json
import os
import re
import time
import argparse
import sys
from urllib.parse import urlparse

import requests
from lxml import html as lxml_html

# ============================================================
# 配置
# ============================================================
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 输入文件
PRODUCT_URLS_FILE = os.path.join(OUTPUT_DIR, "all_product_urls.csv")
INGREDIENT_URLS_FILE = os.path.join(OUTPUT_DIR, "ingredient_urls.csv")

# 输出文件（增量）
PRODUCTS_NDJSON = os.path.join(OUTPUT_DIR, "crawled_products.ndjson")
INGREDIENTS_NDJSON = os.path.join(OUTPUT_DIR, "crawled_ingredients.ndjson")
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "crawl_progress.json")

# 请求设置
REQUEST_DELAY = 1.0       # 每个请求之间的延迟（秒）
REQUEST_TIMEOUT = 30      # 请求超时（秒）
MAX_RETRIES = 3           # 失败重试次数
BATCH_SAVE_INTERVAL = 50  # 每爬取多少个 URL 保存一次进度

# User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


# ============================================================
# 加载已爬取进度
# ============================================================
def load_progress():
    """加载爬取进度，返回已爬取的 URL 集合"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data.get("done_urls", []))
        except (json.JSONDecodeError, KeyError):
            pass
    return set()


def save_progress(done_urls):
    """保存爬取进度"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump({"done_urls": sorted(done_urls)}, f, ensure_ascii=False)


def append_ndjson(filename, data_list):
    """追加数据到 NDJSON 文件"""
    with open(filename, "a", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def count_lines(filename):
    """统计 NDJSON 文件行数"""
    if not os.path.exists(filename):
        return 0
    count = 0
    with open(filename, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count


# ============================================================
# URL 读取
# ============================================================
def read_product_urls():
    """从 all_product_urls.csv 读取所有产品 URL"""
    urls = []
    with open(PRODUCT_URLS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("product_url", "").strip()
            is_discontinued = row.get("is_discontinued", "False").strip() == "True"
            if url:
                urls.append((url, is_discontinued))
    return urls


def read_ingredient_urls():
    """从 ingredient_urls.csv 读取所有成分 URL"""
    urls = []
    with open(INGREDIENT_URLS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("ingredient_url", "").strip()
            if url:
                urls.append(url)
    return urls


# ============================================================
# 页面抓取与解析
# ============================================================
def fetch_page(url, session):
    """抓取页面内容，支持重试"""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.text
            elif resp.status_code == 404:
                print(f"  ⚠️  404 跳过: {url}")
                return None
            elif resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 5))
                print(f"  ⏳  被限速，等待 {wait}s...")
                time.sleep(wait)
                continue
            else:
                print(f"  ⚠️  HTTP {resp.status_code}: {url}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                    continue
                return None
        except requests.RequestException as e:
            last_exc = e
            print(f"  ⚠️  请求失败 (尝试 {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(3)
                continue
    print(f"  ❌  放弃: {url} - {last_exc}")
    return None


def _clean_text(text):
    """清理文本中的多余空白"""
    return re.sub(r"\s+", " ", text).strip()


def _is_header_row(ing_name):
    """判断是否为表格标题行"""
    lower = ing_name.lower().strip()
    header_keywords = [
        "ingredient name", "what-it-does", "what‑it‑does",
        "irritancy", "com.", "irritancy, com.",
        "id-rating", "rating",
    ]
    for kw in header_keywords:
        if lower == kw or lower.startswith(kw):
            return True
    return False


def parse_product_page(html_text, url, is_discontinued=False):
    """解析产品页面，提取结构化数据"""
    tree = lxml_html.fromstring(html_text)

    # 产品名称 - 从 h1 中提取干净的文本
    name = ""
    h1 = tree.xpath("//h1")
    if h1:
        name = _clean_text(h1[0].text_content())
    if not name:
        slug = url.rstrip("/").split("/")[-1]
        name = slug.replace("-", " ").title()

    # 产品图片 - 从 og:image meta 标签获取（最可靠）
    image_url = ""
    og_img = tree.xpath('//meta[@property="og:image"]/@content')
    if og_img:
        image_url = og_img[0].strip()
    if not image_url:
        img_tags = tree.xpath('//div[contains(@class,"product-image")]//img/@src')
        if not img_tags:
            img_tags = tree.xpath('//img[contains(@class,"product")]/@src')
        if not img_tags:
            img_tags = tree.xpath('(//div[contains(@class,"photo") or contains(@class,"image")]//img)[1]/@src')
        if img_tags:
            image_url = img_tags[0].strip()

    # 描述
    description = ""
    desc_elem = tree.xpath('//div[contains(@class,"product-description")]')
    if not desc_elem:
        desc_elem = tree.xpath('//div[contains(@class,"summary")]')
    if desc_elem:
        description = _clean_text(desc_elem[0].text_content())

    # 上传者信息
    uploaded_by = ""
    upload_elem = tree.xpath(
        '//*[contains(text(),"Uploaded by") or contains(text(),"uploaded by")]'
    )
    if upload_elem:
        uploaded_by = _clean_text(upload_elem[0].text_content())

    # 产品亮点标签
    highlights = []
    highlight_elems = tree.xpath(
        '//div[contains(@class,"highlight") or contains(@class,"badge")]//text()'
    )
    for elem in highlight_elems:
        t = elem.strip()
        if t and len(t) > 1:
            highlights.append(t)

    # 成分列表 - 从成分表格中提取
    ingredients = []

    # 方式1: 解析成分表格中的行（排除表头行）
    ingredient_rows = tree.xpath('//table[descendant::a[contains(@href,"ingredients")]]//tr[td]')
    if not ingredient_rows:
        ingredient_rows = tree.xpath('//table//tr[td]')
    if not ingredient_rows:
        # 方式2: 使用简单的列表文本
        ingredient_rows = tree.xpath('//div[contains(@class,"ingredients-list")]//li')

    seen_ingredients = set()

    for row in ingredient_rows:
        cells = row.xpath(".//td")
        if len(cells) < 1:
            continue

        ing_name_cell = cells[0]
        ing_name = _clean_text(ing_name_cell.text_content())

        # 跳过表头列（"Ingredient name", "what-it-does" 等）
        if _is_header_row(ing_name):
            continue
        if not ing_name or len(ing_name) < 2:
            continue

        # 提取成分 URL（必须有成分链接才认为是有效成分）
        ing_url = ""
        link = ing_name_cell.xpath(".//a/@href")
        if link:
            href = link[0]
            if href.startswith("/"):
                href = "https://incidecoder.com" + href
            ing_url = href

        # 跳过没有成分链接且名称看起来像表头/描述的行
        if not ing_url:
            # 如果这一行没有链接，大概率不是成分行
            continue

        if ing_name not in seen_ingredients:
            seen_ingredients.add(ing_name)

            ingredient = {
                "ingredient_name": ing_name,
                "ingredient_url": ing_url,
            }

            # 功能
            if len(cells) >= 2:
                func = _clean_text(cells[1].text_content())
                if func:
                    ingredient["function"] = func

            # 刺激性和致痘性
            if len(cells) >= 3:
                irr_com = _clean_text(cells[2].text_content())
                if irr_com:
                    ingredient["irritancy_comedogenicity"] = irr_com

            # 评级
            if len(cells) >= 4:
                rating = _clean_text(cells[3].text_content())
                if rating:
                    ingredient["rating"] = rating

            ingredients.append(ingredient)

    # 如果表格解析没结果，尝试从简化列表解析
    if not ingredients:
        ing_items = tree.xpath(
            '//div[contains(@class,"ingred") or contains(@class,"ingredients")]'
            '//span[contains(@class,"name") or contains(@class,"ingred-name")]'
        )
        for item in ing_items:
            name_text = item.text_content().strip()
            if name_text and name_text not in seen_ingredients:
                seen_ingredients.add(name_text)
                ing_url = ""
                link = item.xpath(".//a/@href")
                if link:
                    href = link[0]
                    if href.startswith("/"):
                        href = "https://incidecoder.com" + href
                    ing_url = href
                ingredients.append({
                    "ingredient_name": name_text,
                    "ingredient_url": ing_url,
                })

    # 分类成分信息（抗氧化、舒缓等）
    ingredient_categories = {}
    category_sections = tree.xpath(
        '//h3[contains(text(),"Key Ingredients") or contains(text(),"Other Ingredients")]'
    )
    for cat_section in category_sections:
        cat_name = _clean_text(cat_section.text_content())
        cat_items = []
        sibling = cat_section.getnext()
        while sibling is not None and sibling.tag in ("p", "div", "ul", "ol"):
            cat_items.append(_clean_text(sibling.text_content()))
            sibling = sibling.getnext()
        if cat_items:
            ingredient_categories[cat_name] = " ".join(cat_items)

    # 构建结果
    result = {
        "product_name": name,
        "product_url": url,
        "ingredient_count": len(ingredients),
        "ingredients": ingredients,
        "image_url": image_url,
        "description": description,
        "uploaded_by": uploaded_by,
        "highlights": highlights,
        "is_discontinued": is_discontinued,
    }

    if ingredient_categories:
        result["ingredient_categories"] = ingredient_categories

    return result


def parse_ingredient_page(html_text, url):
    """解析成分页面，提取结构化数据"""
    tree = lxml_html.fromstring(html_text)

    # 成分名称
    name = ""
    h1 = tree.xpath("//h1")
    if h1:
        name = _clean_text(h1[0].text_content())
    if not name:
        slug = url.rstrip("/").split("/")[-1]
        name = slug.replace("-", " ").title()

    # 评级标签（紧跟在 h1 后面的 span）
    rating = ""
    rating_span = tree.xpath(
        '//h1/following-sibling::*[1]//span[contains(@class,"superstar") '
        'or contains(@class,"goodie") or contains(@class,"icky")]'
    )
    if rating_span:
        rating = _clean_text(rating_span[0].text_content()).lower()
    # 也尝试相邻的标签
    if not rating:
        rating_texts = tree.xpath(
            '//span[contains(@class,"superstar") or contains(@class,"goodie") '
            'or contains(@class,"icky")]/text()'
        )
        for rt in rating_texts:
            r = rt.strip().lower()
            if r in ("superstar", "goodie", "icky", "irritant"):
                rating = r
                break

    # What-it-does - 从 "What-it-does:" 标签后的文本提取
    what_it_does = ""
    # 方法1: 找包含 "What-it-does:" 的文本节点
    for elem in tree.xpath('//*[contains(text(),"What-it-does")]'):
        text = _clean_text(elem.text_content())
        # 提取冒号后的内容
        m = re.search(r'What-it-does[：:]*\s*(.*)', text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val and val != "buffering":
                what_it_does = val
                break
            what_it_does = val  # buffering 也是有效值
    # 方法2: 从页面顶部的描述中提取
    if not what_it_does:
        wid_spans = tree.xpath(
            '//span[contains(@class,"what-it-does")]/text()'
        )
        if wid_spans:
            what_it_does = _clean_text(wid_spans[0])
    if not what_it_does:
        # 尝试从页面上部的 info 区域提取
        info_paras = tree.xpath(
            '//div[contains(@class,"ingredient-info")]//p'
        )
        for p in info_paras:
            text = _clean_text(p.text_content())
            if text and not text.startswith("Also"):
                what_it_does = text
                break

    # 别名
    also_called = ""
    ac_elem = tree.xpath(
        '//*[contains(text(),"Also-called") or contains(text(),"Also called")]'
    )
    if ac_elem:
        also_called = _clean_text(ac_elem[0].text_content())
        also_called = re.sub(r"^.*?[:：]\s*", "", also_called)

    # 官方 CosIng 信息
    all_functions = ""
    cas_number = ""
    ec_number = ""
    iupac_name = ""
    ph_eur_name = ""
    sccs_opinions = ""

    # 在 "Official CosIng Information" 区域内查找
    cosing_section = tree.xpath(
        '//*[contains(text(),"Official CosIng Information")]'
        '/following-sibling::*[1]'
    )
    if cosing_section:
        section_text = _clean_text(cosing_section[0].text_content())
        # 提取 All Functions
        m = re.search(r'All Functions[：:]\s*(.*?)(?=CAS|$)', section_text, re.IGNORECASE)
        if m:
            all_functions = m.group(1).strip().rstrip(',')
        # 提取 CAS
        m = re.search(r'CAS\s*#*[：:]\s*([\d\-/ ]+)', section_text)
        if m:
            cas_number = m.group(1).strip()
        # 提取 EC
        m = re.search(r'EC\s*#*[：:]\s*([\d\-]+)', section_text)
        if m:
            ec_number = m.group(1).strip()
        # 提取 Ph. Eur. Name
        m = re.search(r'Ph\.?\s*Eur\.?\s*Name[：:]\s*(.*?)(?=Chemical|$)', section_text, re.IGNORECASE)
        if m:
            ph_eur_name = m.group(1).strip()
        # 提取 IUPAC Name
        m = re.search(r'Chemical/IUPAC\s*Name[：:]\s*(.*?)(?=SCCS|$)', section_text, re.IGNORECASE)
        if m:
            iupac_name = m.group(1).strip()
        # 提取 SCCS
        m = re.search(r'SCCS\s*Opinions[：:]\s*(.*)', section_text, re.IGNORECASE)
        if m:
            sccs_opinions = m.group(1).strip()

    # 详细描述 - 在 "Quick Facts" 或 "Geeky Details" 区域
    description = ""

    # 先找 Quick Facts 列表
    quick_facts = []
    qf_heading = tree.xpath('//h3[contains(text(),"Quick Facts")]')
    if qf_heading:
        # 找后续的 ul/li
        next_node = qf_heading[0].getnext()
        while next_node is not None:
            tag = next_node.tag.lower() if hasattr(next_node, 'tag') else ''
            if tag in ('ul', 'ol'):
                for li in next_node.xpath('.//li'):
                    text = _clean_text(li.text_content())
                    # 去掉开头的 "-"
                    text = text.lstrip('- ').strip()
                    if text:
                        quick_facts.append(text)
            elif tag in ('p', 'div'):
                text = _clean_text(next_node.text_content())
                li_text = next_node.xpath('.//li')
                if li_text:
                    pass  # 已经在 ul 中处理了
                elif text and len(text) > 10:
                    quick_facts.append(text)
            elif tag in ('h2', 'h3', 'h4'):
                break  # 遇到下一个标题就停
            next_node = next_node.getnext()

    # 找 Geeky Details 详细描述
    geeky_details = ""
    gd_heading = tree.xpath(
        '//h3[contains(text(),"Geeky Details")]'
        '| //h2[contains(text(),"Geeky Details")]'
    )
    if gd_heading:
        next_node = gd_heading[0].getnext()
        parts = []
        while next_node is not None:
            tag = next_node.tag.lower() if hasattr(next_node, 'tag') else ''
            # 遇到下一个标题或 "Show me some proof" 或 "Products with" 就停止
            text = _clean_text(next_node.text_content())
            if tag in ('h2', 'h3', 'h4'):
                break
            if 'Show me some proof' in text or 'Products with' in text:
                break
            if tag in ('p', 'div', 'ul', 'ol'):
                if text and len(text) > 5:
                    parts.append(text)
            next_node = next_node.getnext()
        geeky_details = "\n\n".join(parts)

    # 组合描述
    desc_parts = []
    if quick_facts:
        desc_parts.append("Quick Facts:\n" + "\n".join(f"- {f}" for f in quick_facts))
    if geeky_details:
        desc_parts.append(geeky_details)
    if desc_parts:
        description = "\n\n".join(desc_parts)

    result = {
        "ingredient_name": name,
        "ingredient_url": url,
        "rating": rating,
        "what_it_does": what_it_does,
        "also_called": also_called,
        "all_functions": all_functions,
        "cas_number": cas_number,
        "ec_number": ec_number,
        "ph_eur_name": ph_eur_name,
        "iupac_name": iupac_name,
        "sccs_opinions": sccs_opinions,
        "description": description[:8000],
    }

    return result


# ============================================================
# 爬取执行
# ============================================================
def crawl_products(max_count=None):
    """爬取产品页面"""
    print("=" * 60)
    print("📦 产品页面爬取")
    print("=" * 60)

    product_urls = read_product_urls()
    print(f"📋 共 {len(product_urls)} 个产品 URL")

    done_urls = load_progress()
    print(f"✅ 已爬取 {len(done_urls)} 个")

    # 过滤已爬取的
    remaining = [(url, disc) for url, disc in product_urls if url not in done_urls]
    print(f"⏳ 待爬取 {len(remaining)} 个")

    if max_count:
        remaining = remaining[:max_count]
        print(f"🔢 本次限制爬取 {len(remaining)} 个")

    if not remaining:
        print("🎉 所有产品已爬取完毕！")
        return

    existing_count = count_lines(PRODUCTS_NDJSON)
    print(f"📄 已有数据: {existing_count} 条")

    session = requests.Session()
    batch_buffer = []
    crawled_in_session = 0

    try:
        for idx, (url, is_discontinued) in enumerate(remaining, 1):
            print(f"  [{idx}/{len(remaining)}] {url}")

            html_text = fetch_page(url, session)
            if html_text is None:
                done_urls.add(url)
                save_progress(done_urls)
                time.sleep(REQUEST_DELAY)
                continue

            try:
                product_data = parse_product_page(html_text, url, is_discontinued)
                batch_buffer.append(product_data)
                done_urls.add(url)
                crawled_in_session += 1
                print(
                    f"    ✅ {product_data.get('product_name', '?')} "
                    f"| {product_data['ingredient_count']} 种成分"
                )
            except Exception as e:
                print(f"    ❌ 解析失败: {e}")
                done_urls.add(url)

            # 批量保存
            if len(batch_buffer) >= BATCH_SAVE_INTERVAL:
                append_ndjson(PRODUCTS_NDJSON, batch_buffer)
                save_progress(done_urls)
                print(f"  💾 已保存 {len(batch_buffer)} 条，累计 {count_lines(PRODUCTS_NDJSON)} 条")
                batch_buffer.clear()

            time.sleep(REQUEST_DELAY)

    except KeyboardInterrupt:
        print("\n⏹️  用户中断爬取")

    finally:
        # 保存剩余批次
        if batch_buffer:
            append_ndjson(PRODUCTS_NDJSON, batch_buffer)
        save_progress(done_urls)
        print(f"\n📊 本次爬取完成: {crawled_in_session} 个产品")
        print(f"📄 总数据: {count_lines(PRODUCTS_NDJSON)} 条")


def crawl_ingredients(max_count=None):
    """爬取成分页面"""
    print("=" * 60)
    print("🧪 成分页面爬取")
    print("=" * 60)

    ingredient_urls = read_ingredient_urls()
    print(f"📋 共 {len(ingredient_urls)} 个成分 URL")

    # 使用单独的状态文件跟踪成分爬取进度
    done_key = "ingredients_done"
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                progress = json.load(f)
        except json.JSONDecodeError:
            progress = {}
    done_urls = set(progress.get(done_key, []))
    print(f"✅ 已爬取 {len(done_urls)} 个")

    remaining = [u for u in ingredient_urls if u not in done_urls]
    print(f"⏳ 待爬取 {len(remaining)} 个")

    if max_count:
        remaining = remaining[:max_count]

    if not remaining:
        print("🎉 所有成分已爬取完毕！")
        return

    existing_count = count_lines(INGREDIENTS_NDJSON)
    print(f"📄 已有数据: {existing_count} 条")

    session = requests.Session()
    batch_buffer = []
    crawled_in_session = 0

    try:
        for idx, url in enumerate(remaining, 1):
            print(f"  [{idx}/{len(remaining)}] {url}")

            html_text = fetch_page(url, session)
            if html_text is None:
                done_urls.add(url)
                progress[done_key] = sorted(done_urls)
                with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                    json.dump(progress, f, ensure_ascii=False)
                time.sleep(REQUEST_DELAY)
                continue

            try:
                ing_data = parse_ingredient_page(html_text, url)
                batch_buffer.append(ing_data)
                done_urls.add(url)
                crawled_in_session += 1
                print(f"    ✅ {ing_data.get('ingredient_name', '?')}")
            except Exception as e:
                print(f"    ❌ 解析失败: {e}")
                done_urls.add(url)

            if len(batch_buffer) >= BATCH_SAVE_INTERVAL:
                append_ndjson(INGREDIENTS_NDJSON, batch_buffer)
                progress[done_key] = sorted(done_urls)
                with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                    json.dump(progress, f, ensure_ascii=False)
                print(f"  💾 已保存 {len(batch_buffer)} 条")
                batch_buffer.clear()

            time.sleep(REQUEST_DELAY)

    except KeyboardInterrupt:
        print("\n⏹️  用户中断爬取")

    finally:
        if batch_buffer:
            append_ndjson(INGREDIENTS_NDJSON, batch_buffer)
        progress[done_key] = sorted(done_urls)
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False)
        print(f"\n📊 本次爬取完成: {crawled_in_session} 个成分")
        print(f"📄 总数据: {count_lines(INGREDIENTS_NDJSON)} 条")


# ============================================================
# 工具：导出为 CSV / JSON
# ============================================================
def export_products_to_csv():
    """将爬取的产品 NDJSON 导出为 CSV"""
    ndjson_file = PRODUCTS_NDJSON
    if not os.path.exists(ndjson_file):
        print("❌ 没有产品数据文件")
        return

    csv_file = os.path.join(OUTPUT_DIR, "crawled_products.csv")
    rows = []
    with open(ndjson_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                product = json.loads(line)
                # 展平：每个成分一行
                if product.get("ingredients"):
                    for ing in product["ingredients"]:
                        rows.append({
                            "product_name": product.get("product_name", ""),
                            "product_url": product.get("product_url", ""),
                            "image_url": product.get("image_url", ""),
                            "ingredient_name": ing.get("ingredient_name", ""),
                            "ingredient_url": ing.get("ingredient_url", ""),
                            "ingredient_function": ing.get("function", ""),
                            "is_discontinued": product.get("is_discontinued", False),
                        })
                else:
                    rows.append({
                        "product_name": product.get("product_name", ""),
                        "product_url": product.get("product_url", ""),
                        "image_url": product.get("image_url", ""),
                        "ingredient_name": "",
                        "ingredient_url": "",
                        "ingredient_function": "",
                        "is_discontinued": product.get("is_discontinued", False),
                    })
            except json.JSONDecodeError:
                continue

    if rows:
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ 已导出 CSV: {csv_file} ({len(rows)} 行)")
    else:
        print("❌ 没有数据可导出")


def export_ingredients_to_csv():
    """将爬取的成分 NDJSON 导出为 CSV"""
    ndjson_file = INGREDIENTS_NDJSON
    if not os.path.exists(ndjson_file):
        print("❌ 没有成分数据文件")
        return

    csv_file = os.path.join(OUTPUT_DIR, "crawled_ingredients.csv")
    rows = []
    with open(ndjson_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ing = json.loads(line)
                rows.append(ing)
            except json.JSONDecodeError:
                continue

    if rows:
        fieldnames = [
            "ingredient_name", "ingredient_url", "rating", "what_it_does",
            "also_called", "all_functions", "cas_number", "ec_number",
            "ph_eur_name", "iupac_name", "description"
        ]
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
        print(f"✅ 已导出 CSV: {csv_file} ({len(rows)} 行)")
    else:
        print("❌ 没有数据可导出")


def export_to_json():
    """将 NDJSON 合并为一个 JSON 数组文件"""
    for ndjson_file, out_name in [
        (PRODUCTS_NDJSON, "crawled_products.json"),
        (INGREDIENTS_NDJSON, "crawled_ingredients.json"),
    ]:
        if not os.path.exists(ndjson_file):
            continue
        data = []
        with open(ndjson_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        out_path = os.path.join(OUTPUT_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 已导出 JSON: {out_path} ({len(data)} 条)")


# ============================================================
# 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="爬取 incidecoder 数据")
    parser.add_argument("--products", action="store_true", help="只爬取产品")
    parser.add_argument("--ingredients", action="store_true", help="只爬取成分")
    parser.add_argument("--max", type=int, default=None, help="限制爬取数量")
    parser.add_argument("--clean", action="store_true", help="清空进度重新爬取")
    parser.add_argument("--export", action="store_true", help="导出为 CSV/JSON")
    args = parser.parse_args()

    if args.clean:
        for f in [PROGRESS_FILE]:
            if os.path.exists(f):
                os.remove(f)
                print(f"🧹 已删除进度文件: {f}")
        # 也清空已爬取的数据文件（保留初始的 products.ndjson）
        for f in [PRODUCTS_NDJSON, INGREDIENTS_NDJSON]:
            if os.path.exists(f):
                os.remove(f)
                print(f"🧹 已删除数据文件: {f}")
        print("✅ 已清空所有爬取进度和数据")
        # 如果只传了 --clean，不执行爬取
        if not args.products and not args.ingredients and not args.export:
            return

    if args.export:
        export_products_to_csv()
        export_ingredients_to_csv()
        export_to_json()
        return

    # 默认同时爬取产品和成分
    do_products = args.products or (not args.products and not args.ingredients)
    do_ingredients = args.ingredients or (not args.products and not args.ingredients)

    if do_products:
        crawl_products(args.max)
    if do_ingredients:
        crawl_ingredients(args.max)

    print("\n" + "=" * 60)
    print("🏁 全部完成！")
    print(f"   📄 产品数据: {count_lines(PRODUCTS_NDJSON)} 条")
    print(f"   📄 成分数据: {count_lines(INGREDIENTS_NDJSON)} 条")
    print(f"   📊 进度文件: {PROGRESS_FILE}")
    print("=" * 60)
    print("💡 提示: 运行 python crawl_data.py --export 导出为 CSV/JSON")


if __name__ == "__main__":
    main()
