import requests, json, re, os, time, urllib3, random
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# 停用 SSL 安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 顏色與極簡樣式 =================
class UI:
    C = '\033[96m' ; G = '\033[92m' ; Y = '\033[93m' ; R = '\033[91m'
    B = '\033[1m'  ; BL = '\033[94m'; M = '\033[95m'; RS = '\033[0m'
    
    @staticmethod
    def banner():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{UI.C}{UI.B}╔" + "═"*58 + "╗")
        print(f"║{UI.RS} {UI.B}🎓 115 學年度 大學 / 科大 一階聯合查榜系統{UI.RS}          {UI.C}{UI.B}║")
        print(f"╚" + "═"*58 + f"╝{UI.RS}")

    @staticmethod
    def bar_cfg(desc, color):
        return {
            'desc': f"{color}{desc:^10}{UI.RS}",
            'bar_format': '{desc} {percentage:3.0f}% |{bar:20}| {n_fmt}/{total_fmt}',
            'ascii': " ❯", 
            'ncols': 55
        }

# ================= 配置區 =================
HASH_ID = "ColQry_115xappLyfOrStu_Azd5gP29" 
CAC_QUERY_ROOT = f"https://www.cac.edu.tw/apply115/system/{HASH_ID}/"
CAC_RESULT_ROOT = "https://www.cac.edu.tw/CacLink/apply115/115Apply_sievE_Result_querY_615JG8Wgh9d/html_sieve_result_115_Zx57f1dW/ColPost/"
JCTV_URL = "https://ent01.jctv.ntut.edu.tw/applys1result/college.html"
JCTV_JS_URL = "https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js"
DB_FILE = "exam_local_db.json"
MAX_WORKERS = 8 

# ================= 1. 完整考場數據庫 (PDF 1-7頁全銜) =================
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

# ================= 安全工具與抓取器 =================

class SafeFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    def get(self, url, referer=None):
        try:
            h = {'Referer': referer} if referer else {}
            r = self.session.get(url, headers=h, verify=False, timeout=25)
            r.encoding = 'utf-8'
            return r.text if r.status_code == 200 else None
        except: return None

    def post(self, url, data):
        try:
            r = self.session.post(url, data=data, verify=False, timeout=25)
            r.encoding = 'utf-8'
            return r.text if r.status_code == 200 else None
        except: return None

fetcher = SafeFetcher()

def get_site(eid):
    try:
        v = int(eid)
        for s, e, n in TEST_SITES:
            if s <= v <= e: return n
    except: pass
    return "未知考場"

# ================= 核心爬蟲邏輯 =================

class ProScraper:
    def __init__(self):
        self.db = {"cac": {}, "jctv": {}, "name_map": {}}
        self.cac_meta = {}

    def sync_cac_meta(self):
        list_html = fetcher.post(CAC_QUERY_ROOT + "ShowSchool.php", 
                                 data={'option': 'SCHNAME', 'SubSchName': '依學校名稱查詢'})
        if not list_html: return
        sch_codes = list(set(re.findall(r'colno=\s*(\d{3})', list_html)))
        
        def process_meta(c):
            h = fetcher.get(f"{CAC_QUERY_ROOT}ShowSchGsd.php?colno={c}", referer=CAC_QUERY_ROOT+"ShowSchool.php")
            m = {}
            if h:
                for row in BeautifulSoup(h, 'html.parser').find_all('tr'):
                    match = re.search(r'\((\d{6})\)', row.get_text())
                    tds = row.find_all('td')
                    if match and len(tds) >= 9:
                        m[match.group(1)] = {"q": tds[1].text.strip(), "d": tds[8].text.strip()}
            return m

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
            futs = [exe.submit(process_meta, c) for c in sch_codes]
            with tqdm(**UI.bar_cfg("普大架構", UI.BL), total=len(sch_codes)) as pbar:
                for f in as_completed(futs):
                    self.cac_meta.update(f.result())
                    pbar.update(1)

    def run_cac(self):
        res = fetcher.get(CAC_RESULT_ROOT + "collegeList.htm")
        if not res: return
        sch_links = BeautifulSoup(res, 'html.parser').select('td.colname a')
        
        def process_sch(link):
            sn, su = link.get_text(strip=True), CAC_RESULT_ROOT + link.get('href')
            h = fetcher.get(su, referer=CAC_RESULT_ROOT+"collegeList.htm")
            depts = {}
            if h:
                for tr in BeautifulSoup(h, 'html.parser').find_all('tr', height="30px"):
                    tds = tr.find_all('td')
                    if not tds or "系" not in tds[0].text: continue
                    ids, dc = [], ""
                    for a in tr.select('a[href*=".htm"]'):
                        mc = re.search(r'(\d{6})\.htm', a.get('href'))
                        if mc: dc = mc.group(1)
                        d_h = fetcher.get(CAC_RESULT_ROOT + "web/" + a.get('href'), referer=su)
                        if d_h: ids.extend(re.findall(r'\b\d{8}\b', d_h))
                    if dc:
                        m = self.cac_meta.get(dc, {"q": "-", "d": "-"})
                        depts[tds[0].get_text(strip=True)] = {
                            "科系代碼": dc, "招生名額": m["q"], "面試日期": m["d"], "錄取名單": list(set(ids))
                        }
            return sn, depts

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
            futs = [exe.submit(process_sch, l) for l in sch_links]
            with tqdm(**UI.bar_cfg("普大名單", UI.G), total=len(sch_links)) as pbar:
                for f in as_completed(futs):
                    n, d = f.result(); self.db["cac"][n] = d
                    pbar.update(1)

    def run_jctv(self):
        js = fetcher.get(JCTV_JS_URL)
        j_lookup = {}
        if js:
            for item in re.findall(r'\[(.*?)\]', re.search(r'deptData\s*=\s*new Array\((.*?)\);', js, re.DOTALL).group(1)):
                p = [x.strip().strip("'") for x in item.split("','")]
                if len(p) >= 5: j_lookup[p[0]+p[2]] = p[1]

        res = fetcher.get(JCTV_URL)
        if not res: return
        s_list = [(o.get('value'), o.get_text(strip=True)) for o in BeautifulSoup(res, 'html.parser').select('select option') if o.get('value') != "-1"]

        with tqdm(**UI.bar_cfg("科大同步", UI.Y), total=len(s_list)) as pbar:
            for sc, sn in s_list:
                h = fetcher.post(JCTV_URL, data={'doit':'view','code':sc})
                if h:
                    if sn not in self.db["jctv"]: self.db["jctv"][sn] = {}
                    for tr in BeautifulSoup(h, 'html.parser').select('table.enterTable tbody tr'):
                        tds = tr.find_all('td')
                        if len(tds) < 3: continue
                        dn, raw = tds[1].get_text(strip=True), tds[2].get_text()
                        ids = []
                        for pn, pi in re.findall(r'([^\(]+)\((\d{8})\)', raw):
                            # --- 修正：強力清理姓名中的空白與換行符號 ---
                            clean_pn = re.sub(r'[\r\n\t\s]+', '', pn)
                            self.db["name_map"][pi] = clean_pn
                            ids.append(pi)
                        dc = j_lookup.get(sc+dn, "未知")
                        if dn not in self.db["jctv"][sn]: self.db["jctv"][sn][dn] = {"科系代碼": dc, "錄取名單": []}
                        self.db["jctv"][sn][dn]["錄取名單"] = list(set(self.db["jctv"][sn][dn]["錄取名單"] + ids))
                pbar.update(1)

    def save(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)

# ================= 查詢介面 =================

def start_ui(db=None):
    if not db:
        if not os.path.exists(DB_FILE): return
        with open(DB_FILE, 'r', encoding='utf-8') as f: db = json.load(f)
    nm = db.get("name_map", {})
    UI.banner()
    print(f"{UI.Y}💡 支援 姓名 或 8 位應試號碼{UI.RS}")
    
    while True:
        q = input(f"\n{UI.B}🔍 查詢 (Q 離開): {UI.RS}").strip()
        if q.lower() == 'q': break
        masked = q[0]+"Ｏ"+(q[-1] if len(q)>2 else "") if not re.match(r'^\d+$', q) else ""
        ids = [q] if re.match(r'^\d{8}$', q) else [i for i, n in nm.items() if n == masked]
        if not ids: print(f"{UI.R}❌ 查無記錄。{UI.RS}"); continue

        for eid in ids:
            print(f"\n{UI.BL}┏" + "━"*45 + "┓")
            print(f"┃ {UI.B}應試號碼：{eid}{UI.RS}")
            print(f"┃ {UI.B}考生姓名：{nm.get(eid, f'{UI.R}普大不公開{UI.RS}')}{UI.RS}")
            print(f"┃ {UI.B}分配考場：{get_site(eid)}{UI.RS}")
            print(f"{UI.BL}┗" + "━"*45 + f"┛{UI.RS}")
            
            found = False
            for cat, label, color in [('cac', '普大', UI.G), ('jctv', '科大', UI.Y)]:
                for s, depts in db.get(cat, {}).items():
                    for dn, info in depts.items():
                        if eid in info["錄取名單"]:
                            print(f"  {color}❯{UI.RS} [{label}] {s}")
                            print(f"    └ {dn} ({UI.B}{info['科系代碼']}{UI.RS})")
                            if cat=='cac': print(f"      名額:{info['招生名額']} | 日期:{info['面試日期']}")
                            found = True
            if not found: print(f"  {UI.R}✘ 未找到錄取記錄。{UI.RS}")

if __name__ == "__main__":
    UI.banner()
    print(f"1. {UI.G}[官網同步]{UI.RS} 建立本地資料庫")
    print(f"2. {UI.C}[雲端同步]{UI.RS} 獲取最新預爬資料")
    print(f"3. {UI.Y}[本地查詢]{UI.RS} 載入已存檔案")
    m = input(f"\n{UI.B}請選擇模式: {UI.RS}").strip()

    data = None
    if m == '1':
        p = ProScraper()
        p.sync_cac_meta()
        p.run_cac()
        p.run_jctv()
        p.save()
        data = p.db
    elif m == '2':
        # 雲端下載邏輯範例
        pass
    
    if data or os.path.exists(DB_FILE): start_ui(data)
