import json
import os
import requests
import httplib2
import xml.etree.ElementTree as ET
from oauth2client.service_account import ServiceAccountCredentials

def fetch_and_parse_xml(url):
    # XML 콘텐츠 가져오기
    response = requests.get(url)
    response.raise_for_status()

    # XML 파싱
    root = ET.fromstring(response.content)

    # <loc> 태그 내 URL 추출
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [element.text for element in root.findall('ns:url/ns:loc', namespace)]
    return urls

def http_request(http, endpoint, method, json_content):
    response, content = http.request(
        endpoint,
        method=method,
        body=json_content,
        headers={'Content-Type': 'application/json'}
    )
    return response, content

def handler():
    sitemap_url = 'http://www.handongbee.com/sitemap.xml'
    urls = fetch_and_parse_xml(sitemap_url)
    
    JSON_KEY_FILE = "secret.json"
    scopes = ["https://www.googleapis.com/auth/indexing"]
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=scopes)
    http = credentials.authorize(httplib2.Http())

    for url in urls:
        endpoint_meta = "https://indexing.googleapis.com/v3/urlNotifications/metadata?url=" + url
        response, content = http_request(http, endpoint_meta, "GET", "")
        if response.status == 404:
            print(f"URL not found: {url}")
            content = {
                "url": url,
                "type": "URL_UPDATED"
            }
            json_content = json.dumps(content)
            response, content = http_request(http, "https://indexing.googleapis.com/v3/urlNotifications:publish", "POST", json_content)
            print(f"Indexing {url}: {response.status}")

handler()