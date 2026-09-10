#!/usr/bin/env python3
import csv, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, unquote
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (compatible; NGXPublicArchive/1.0; +https://github.com/NgwutaOforbuike/PROJECTS-21)"
SITEMAPS = [
    "https://ngxgroup.com/wp-sitemap.xml",
    "https://ngxgroup.com/sitemap_index.xml",
    "https://ngxgroup.com/sitemap.xml",
]
SEED_PAGES = [
    "https://ngxgroup.com/exchange/data/corporate-disclosures",
    "https://ngxgroup.com/ngx-download-category/annual-reports",
    "https://ngxgroup.com/ngx-download-category/corporate-disclosures",
]
DOC_EXTS = (".pdf",".xlsx",".xls",".docx",".doc",".csv",".zip")
KEYWORDS = (
    "ngx-download","corporate-disclosure","financial","annual-report","annual-reports",
    "interim","unaudited","audited","result","company-results","dividend","agm","egm",
    "prospectus","rights-issue","scheme","merger","delisting","listing","free-float",
    "insider","shareholding","board","management-change","corporate-action"
)
session = requests.Session()
session.headers.update({"User-Agent":UA, "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})

def get(url, timeout=25):
    try:
        r=session.get(url,timeout=timeout,allow_redirects=True)
        if r.status_code==200:
            return r
    except Exception:
        pass
    return None

def parse_sitemap(url, seen, pages, direct_docs, depth=0):
    if url in seen or depth>3: return
    seen.add(url)
    r=get(url)
    if not r: return
    txt=r.text
    try:
        root=ET.fromstring(txt)
        locs=[e.text.strip() for e in root.iter() if e.tag.endswith("loc") and e.text]
    except Exception:
        locs=re.findall(r"<loc>(.*?)</loc>",txt,re.I|re.S)
    for loc in locs:
        low=loc.lower()
        if low.endswith(".xml") or "sitemap" in low:
            parse_sitemap(loc,seen,pages,direct_docs,depth+1)
        elif any(low.split("?")[0].endswith(ext) for ext in DOC_EXTS):
            direct_docs.add((loc,url))
        else:
            pages.add(loc)

def extract_links(page_url):
    r=get(page_url)
    if not r: return []
    soup=BeautifulSoup(r.text,"html.parser")
    out=[]
    for tag in soup.find_all(["a","iframe","embed","source"]):
        href=tag.get("href") or tag.get("src")
        if not href: continue
        u=urljoin(r.url,href.strip())
        out.append(u)
    # catch raw URLs embedded in scripts/JSON
    for u in re.findall(r'https?://[^"\'<>\s]+',r.text):
        out.append(u.replace("\\/","/"))
    return out

def classify(url):
    s=unquote(url).lower()
    if any(k in s for k in ["annual","quarter_5","audited"]): return "Annual/Audited"
    if any(k in s for k in ["quarter_1","quarter_2","quarter_3","quarter_4","interim","unaudited"]): return "Interim/Unaudited"
    if "dividend" in s or "corporate_action" in s or "corporate-action" in s: return "Corporate Action/Dividend"
    if "agm" in s or "egm" in s: return "AGM/EGM"
    if any(k in s for k in ["prospectus","rights","offer"]): return "Offer/Prospectus"
    if any(k in s for k in ["merger","scheme","acquisition"]): return "M&A/Scheme"
    if any(k in s for k in ["delist","suspension"]): return "Delisting/Suspension"
    return "Other Filing/Disclosure"

def is_doc(u):
    try:
        p=urlparse(u)
    except Exception:
        return False
    low=p.path.lower()
    host=p.netloc.lower()
    if any(low.endswith(ext) for ext in DOC_EXTS): return True
    if host=="doclib.ngxgroup.com" and ("financial_newsdocs" in low or "documents" in low): return True
    return False

def main():
    seen=set(); pages=set(); docs=set()
    for sm in SITEMAPS:
        parse_sitemap(sm,seen,pages,docs)
    pages.update(SEED_PAGES)

    candidates=[u for u in pages if any(k in u.lower() for k in KEYWORDS)]
    # include all ngx-download pages from sitemap
    candidates=list(dict.fromkeys(candidates))
    print(f"sitemap pages={len(pages)} candidate_pages={len(candidates)} direct_docs={len(docs)}")

    found={}
    for u,src in docs:
        found[u]=src

    with ThreadPoolExecutor(max_workers=18) as ex:
        futs={ex.submit(extract_links,u):u for u in candidates}
        done=0
        for fut in as_completed(futs):
            src=futs[fut]; done+=1
            try: links=fut.result()
            except Exception: links=[]
            for u in links:
                if is_doc(u):
                    found.setdefault(u,src)
            if done%250==0:
                print(f"scanned {done}/{len(candidates)}; docs={len(found)}")

    rows=[]
    for u,src in sorted(found.items()):
        path=unquote(urlparse(u).path)
        filename=path.rsplit("/",1)[-1] or "document"
        rows.append({
            "url":u,
            "host":urlparse(u).netloc,
            "filename":filename,
            "category":classify(u),
            "source_page":src,
        })

    with open("ngx_manifest.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["url","host","filename","category","source_page"])
        w.writeheader(); w.writerows(rows)
    with open("ngx_urls.txt","w",encoding="utf-8") as f:
        for r in rows: f.write(r["url"]+"\n")
    with open("ngx_discovery_summary.txt","w",encoding="utf-8") as f:
        f.write(f"sitemap_pages={len(pages)}\n")
        f.write(f"candidate_pages_scanned={len(candidates)}\n")
        f.write(f"documents_discovered={len(rows)}\n")
    print(f"documents_discovered={len(rows)}")

if __name__=="__main__":
    main()
