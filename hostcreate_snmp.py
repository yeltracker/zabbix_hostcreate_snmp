import pandas as pd
import requests
import json

ZABBIX_URL = "http://zabbix.url.com/zabbix/api_jsonrpc.php" 
USERNAME = "USERNAME"  
PASSWORD = "PASSWORD"

# Data Collection menüsünden host group ve templates sekmelerinden bulabilrsiniz. Değerler sabit olmalıdır. Integer değer olmalıdır. 
GROUP_ID = 000
TEMPLATE_ID = 00000

def login_to_zabbix():
    headers = {'Content-Type': 'application/json'}
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": USERNAME,
            "password": PASSWORD
        },
        "id": 1,
        "auth": None
    }

    response = requests.post(ZABBIX_URL, headers=headers, json=data)
    result = response.json()
    if "result" in result:
        print("Zabbix'e başarıyla giriş yapıldı! Auth token:", result["result"])
        return result["result"]
    else:
        print("Zabbix'e giriş yapılamadı. Hata:", result)
        return None

def add_host_to_zabbix(auth_token, hostname, ip):
    headers = {'Content-Type': 'application/json'}
    data = {
        "jsonrpc": "2.0",
        "method": "host.create",
        "params": {
            "host": hostname,
            "interfaces": [{
                "type": 2,      
                "main": 1,
                "useip": 1,
                "ip": str(ip),
                "dns": "",
                "port": "161",
                "details": {
                    "version": 2,                   # SNMPv2
                    "community": "{$SNMP_COMMUNITY}", # Community makro
                    "bulk": 1,
                    "retries": 1,
                    "timeout": 1
                }
            }],
            "groups": [{"groupid": GROUP_ID}],
            "templates": [{"templateid": TEMPLATE_ID}],
            "macros": [
                {"macro": "{$SNMP_COMMUNITY}", "value": "!_LÜTFEN BURAYI DEĞİŞTİRİNİZ. COMMUNITY SIFRENIZI YAZMALISINIZ._!"},
                {"macro": "{$MAX_REPETITIONS}", "value": "10"}  # Max repetition count değeridir.
            ],
            "status": 0
        },
        "auth": auth_token,
        "id": 1
    }

    response = requests.post(ZABBIX_URL, headers=headers, json=data)
    result = response.json()
    print("API Yanıtı:", json.dumps(result, indent=4))
    return result

def read_excel(file_path):
    df = pd.read_excel(file_path)
    print("Excel sütun adları:", df.columns)
    # Excel'deki boş hostname veya IP satırlarını kaldırması içindir.
    df = df.dropna(subset=['Hostname', 'IP'])
    return df

def main():
    auth_token = login_to_zabbix()
    if not auth_token:
        return

    file_path = "EXCELDOSYANİZ.xlsx"
    df = read_excel(file_path)

    for index, row in df.iterrows():
        hostname = row['Hostname']
        ip = row['IP']

        print(f"{hostname} ({ip}) ekleniyor...")

        result = add_host_to_zabbix(auth_token, hostname, ip)
        if "result" in result:
            print(f"Host {hostname} başarıyla eklendi!\n")
        else:
            print(f"{hostname} eklenirken bir hata oluştu: {json.dumps(result, indent=4)}\n")

if __name__ == "__main__":
    main()
