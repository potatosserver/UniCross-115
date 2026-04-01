import requests, json, re, os, time, urllib3
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# 停用 SSL 安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. 完整考場數據庫 (PDF 1-7頁全銜)
# ==========================================
TEST_SITES = [
    (11000101, 11006036, "臺北市立大同高中"), (11006101, 11009236, "臺北市立建國高中"), (14110101, 14110103, "臺北市立建國高中"),
    (11009301, 11012736, "臺北市立第一女中"), (11012801, 11016136, "臺北市立西松高中"), (11016201, 11020836, "臺北市立和平高中"),
    (19110101, 19112608, "國立臺灣大學"), (11020901, 11024836, "國立臺灣師大附中"), (11024901, 11028836, "臺北市立松山高中"),
    (11028901, 11032836, "臺北市立成淵高中"), (11032901, 11036336, "臺北市立華江高中"), (11036401, 11038836, "國立臺灣師範大學"),
    (19120101, 19121101, "國立臺灣師範大學"), (11038901, 11041636, "臺北市立中山女高"), (11041701, 11043617, "臺北市立景美女中"),
    (11043701, 11047536, "臺北市立百齡高中"), (11047601, 11051136, "臺北市立內湖高中"), (11051201, 11054136, "臺北市立木柵高工"),
    (11054201, 11056836, "新北市立新店高中"), (11056901, 11060336, "臺北市立陽明高中"), (11060401, 11063336, "臺北市立復興高中"),
    (11063401, 11068336, "國立華僑高中"), (19250101, 19250407, "國立華僑高中"), (11068401, 11073523, "新北市立海山高中"),
    (14250101, 14250104, "新北市立海山高中"), (11073601, 11078536, "新北市立板橋高中"), (19250501, 19251205, "新北市立板橋高中"),
    (11078601, 11083536, "新北市立新莊高中"), (19251301, 19251507, "新北市立新莊高中"), (11083601, 11089332, "新北市立丹鳳高中"),
    (14250201, 14250201, "新北市立丹鳳高中"), (19251601, 19251902, "新北市立丹鳳高中"), (11089401, 11093915, "新北市立新北高中"),
    (14260101, 14260102, "新北市立新北高中"), (19260101, 19260409, "新北市立新北高中"), (11094001, 11098236, "新北市立三民高中"),
    (11098301, 11103536, "新北市立永平高中"), (11103601, 11108630, "新北市立錦和高中"), (11108701, 11110136, "新北市立光復高中"),
    (11110201, 11112716, "國立臺灣海洋大學"), (11112801, 11114936, "國立基隆女中"), (11115001, 11118836, "桃園市立武陵高中"),
    (11118901, 11123336, "桃園市立陽明高中"), (11123401, 11128236, "桃園市立桃園高中"), (11128301, 11131426, "國立北科大附屬桃園農工"),
    (11131501, 11135236, "國立中央大學附屬中壢高中"), (11135301, 11139136, "私立復旦高中"), (11139201, 11143036, "私立育達高中"),
    (11143101, 11146436, "桃園市立平鎮高中"), (11146501, 11149108, "桃園市立大園國際高中"), (11149201, 11152136, "國立新竹高中"),
    (11152201, 11155936, "國立新竹女中"), (11156001, 11159636, "私立曙光女中"), (11159701, 11163206, "新竹市立香山高中"),
    (11163301, 11167622, "國立陽明交大附中"), (11167701, 11171730, "國立苗栗高中"), (11171801, 11176036, "臺中市立文華高中"),
    (11176101, 11181236, "臺中市立臺中二中"), (11181301, 11186836, "臺中市立臺中一中"), (11186901, 11191036, "國立中興大學附中"),
    (11191101, 11195836, "私立明德高中"), (11195901, 11198016, "靜宜大學"), (11198101, 11201636, "臺中市立清水高中"),
    (11201701, 11207615, "私立弘文高中"), (11207701, 11212136, "臺中市立臺中女中"), (11212201, 11216326, "臺中市立惠文高中"),
    (11216401, 11219305, "國立中興高中"), (11219401, 11220836, "私立同德高中"), (11220901, 11223615, "國立彰化師範大學"),
    (11223701, 11228436, "國立彰化師大附屬高工"), (11228501, 11231419, "國立員林高中"), (11231501, 11233936, "國立員林崇實高工"),
    (11234001, 11237436, "國立斗六高中"), (11237501, 11240831, "國立虎尾高中"), (11240901, 11246230, "國立嘉義高中"),
    (11246301, 11250436, "國立嘉義女中"), (11250501, 11253935, "國立臺南一中"), (11254001, 11259036, "國立臺南二中"),
    (11259101, 11263136, "國立臺南女中"), (11263201, 11267736, "國立家齊高中"), (11267801, 11272936, "私立長榮高中"),
    (11273001, 11276208, "國立新營高中"), (11276301, 11279019, "國立高雄師範大學"), (11279101, 11281036, "國立高雄師大附中"),
    (11281101, 11284536, "高雄市立中正高中"), (11284601, 11289236, "國立鳳新高中"), (11289301, 11294636, "私立道明高中"),
    (11294701, 11299236, "高雄市立高雄高中"), (11299301, 11303736, "高雄市立高雄女中"), (11303801, 11307631, "高雄市立中山高中"),
    (11307701, 11312236, "高雄市立左營高中"), (11312301, 11314734, "國立屏東大學"), (11314801, 11316436, "國立屏東大學(屏師校區)"),
    (11316501, 11319836, "國立屏東女中"), (11319901, 11326235, "國立宜蘭大學"), (11326301, 11328436, "國立花蓮高中"),
    (11328501, 11330514, "國立花蓮女女中"), (11330601, 11332810, "國立臺東女中"), (11332901, 11333523, "國立澎湖科技大學"),
    (11333601, 11334531, "國立金門大學"), (11334601, 11334708, "國立馬祖高中")
]

# --- 2. 配置 ---
DB_FILE = "exam_local_db.json"
REMOTE_DB_URL = "https://raw.githubusercontent.com/potatosserver/Tools/refs/heads/main/exam_local_db.json"
MAX_WORKERS = 15
JCTV_COOKIES = {'JSESSIONID': '560F695994077E8A9969AD2525D56EA1'} 

CAC_ROOT = "https://www.cac.edu.tw/CacLink/apply115/115Apply_sievE_Result_querY_615JG8Wgh9d/html_sieve_result_115_Zx57f1dW/ColPost/"
JCTV_URL = "https://ent01.jctv.ntut.edu.tw/applys1result/college.html"

# ==========================================
# 3. 功能函式 (抓取與解析)
# ==========================================

def fetch_html(url, method="GET", data=None, referer=None, is_jctv=False):
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    if referer: h['Referer'] = referer
    try:
        cookies = JCTV_COOKIES if is_jctv else None
        if method == "POST":
            r = requests.post(url, headers=h, data=data, cookies=cookies, verify=False, timeout=15)
        else:
            r = requests.get(url, headers=h, verify=False, timeout=15)
        r.encoding = 'utf-8'
        return r.text if r.status_code == 200 else None
    except: return None

def process_cac_school(s_link):
    name, url = s_link.get_text(strip=True), CAC_ROOT + s_link.get('href')
    html = fetch_html(url, referer=CAC_ROOT+"collegeList.htm")
    depts = {}
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.find_all('tr', height="30px"):
            tds = tr.find_all('td')
            if not tds or "系" not in tds[0].text: continue
            ids = []
            for a in tr.select('a[href*="common/"], a[href*="extra/"]'):
                d_html = fetch_html(CAC_ROOT + "web/" + a.get('href'), referer=url)
                if d_html: ids.extend(re.findall(r'\b\d{8}\b', d_html))
            if ids: depts[tds[0].get_text(strip=True)] = list(set(ids))
    return name, depts

def process_jctv_school(s_info):
    code, name = s_info
    html = fetch_html(JCTV_URL, "POST", {'doit':'view','code':code}, JCTV_URL, True)
    depts, names = {}, {}
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for tr in soup.select('table.enterTable tbody tr'):
            tds = tr.find_all('td')
            if len(tds) < 3: continue
            d_name = tds[1].get_text(strip=True)
            # 強力清理不可見字元
            raw = tds[2].get_text(separator=" ", strip=True).replace("\n","").replace("\r","").replace("\t","").replace(" ","")
            m = re.search(r'([^\(]+)\((\d{8})\)', raw)
            if m:
                p_n, p_i = m.group(1), m.group(2)
                names[p_i] = p_n
                if d_name not in depts: depts[d_name] = []
                depts[d_name].append(p_i)
    return name, depts, names

# ==========================================
# 4. 同步與搜尋模式
# ==========================================

def start_sync():
    print("\n🚀 [模式1] 啟動高速官網同步...")
    res = fetch_html(CAC_ROOT + "collegeList.htm")
    if not res: return None
    cac_links = BeautifulSoup(res, 'html.parser').select('td.colname a')
    
    cac_db = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futs = {exe.submit(process_cac_school, l): l for l in cac_links}
        for f in tqdm(as_completed(futs), total=len(cac_links), desc="普大同步"):
            n, d = f.result(); cac_db[n] = d

    j_main = fetch_html(JCTV_URL)
    if not j_main: return None
    s_list = [(o.get('value'), o.get_text(strip=True)) for o in BeautifulSoup(j_main, 'html.parser').select('select option') if o.get('value') != "-1"]
    
    jctv_db, name_map = {}, {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futs = {exe.submit(process_jctv_school, s): s for s in s_list}
        for f in tqdm(as_completed(futs), total=len(s_list), desc="科大同步"):
            n, d, nm = f.result(); jctv_db[n] = d; name_map.update(nm)

    full_db = {"cac": cac_db, "jctv": jctv_db, "name_map": name_map}
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_db, f, ensure_ascii=False, indent=2) # 修正：加入 indent 讓 JSON 易讀
    return full_db

def run_cloud():
    print(f"\n📡 [模式2] 正在從 GitHub 同步預爬資料庫...")
    try:
        r = requests.get(REMOTE_DB_URL, verify=False, timeout=20)
        return r.json() if r.status_code == 200 else None
    except: return None

def mask_name(name):
    if len(name) < 2: return name
    if "Ｏ" in name: return name
    return name[0] + "Ｏ" + (name[-1] if len(name) > 2 else "")

def get_site(num):
    v = int(num)
    for s, e, n in TEST_SITES:
        if s <= v <= e: return n
    return "未知考場"

def start_ui(db):
    nm_map = db.get("name_map", {})
    print("\n" + "═"*60 + "\n🎓 115 學年度 聯合查榜系統 (本地+網頁 雙模式)\n" + "═"*60)
    print("💡 支援輸入: 8位應試號碼 或 姓名(如: 趙學群)")
    while True:
        query = input("\n請輸入查詢 (Q 離開): ").strip()
        if query.lower() == 'q': break
        
        target_ids = []
        if re.match(r'^\d{8}$', query):
            target_ids = [query]
        else:
            m_name = mask_name(query)
            target_ids = [eid for eid, n in nm_map.items() if n == m_name]
            if not target_ids:
                print(f"❌ 找不到「{m_name}」的紀錄。")
                continue

        for eid in target_ids:
            name = nm_map.get(eid, "（無姓名記錄）")
            site = get_site(eid)
            print(f"\n【考生資訊】號碼: {eid} | 姓名: {name} | 考場: {site}")
            found = False
            for k, l in [('cac', '普大'), ('jctv', '科大')]:
                for s, depts in db.get(k, {}).items():
                    for d, ids in depts.items():
                        if eid in ids:
                            print(f"  ✅ [{l}] {s} - {d}")
                            found = True
            if not found: print("  ❌ 未找到通過記錄")

# ==========================================
# 5. 主程序入口
# ==========================================
if __name__ == "__main__":
    print("歡迎使用 115學年度一階查榜工具")
    print("-" * 35)
    print("1. [官網下載] 即時高速抓取 (需更新 Cookie)")
    print("2. [雲端下載] 從 GitHub 獲取預爬 JSON")
    print("3. [本地查詢] 直接使用本地檔案")
    print("-" * 35)
    mode = input("請選擇模式 (1/2/3): ").strip()

    db = None
    if mode == '1':
        db = start_sync()
    elif mode == '2':
        db = run_cloud()
    elif mode == '3':
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                db = json.load(f)
        else:
            print("❌ 本地無資料，請先選模式 1 或 2")

    if db: start_ui(db)
    else: print("❌ 啟動失敗，請檢查網路或 Cookie。")
