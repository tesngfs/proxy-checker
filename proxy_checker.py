import sys
import requests
import socks
import socket
from concurrent.futures import ThreadPoolExecutor

class ProxyChecker:
    def __init__(self, file_path):
        self.file_path = file_path

    def check_proxy(self, proxy):
        try:
            if proxy.startswith("http://"):
                response = requests.get('http://www.google.com', proxies={"http": proxy}, timeout=10)
            elif proxy.startswith("https://"):
                response = requests.get('https://www.google.com', proxies={"https": proxy}, timeout=10)
            elif len(proxy.split(':')) == 4:
                ip, port, username, password = proxy.split(':')
                socks.set_default_proxy(socks.SOCKS5, ip, int(port), username=username, password=password)
                socket.socket = socks.socksocket
                response = requests.get('http://www.google.com', timeout=10)
            elif len(proxy.split(':')) == 2:
                ip, port = proxy.split(':')
                socks.set_default_proxy(socks.SOCKS5, ip, int(port))
                socket.socket = socks.socksocket
                response = requests.get('http://www.google.com', timeout=10)
            else:
                print("Invalid proxy format")
                return None

            if response.status_code == 200:
                print(f'[+] Working proxy: {proxy}')
                return proxy  
            else:
                print(f'[-] Invalid proxy: {proxy}')
                return None
        except Exception as e:
            print(f'[-] Failed to connect using proxy: {proxy}, Error: {e}')
            return None

    def remove_duplicates(self):
        if self.file_path:
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
            lines = list(set(lines))
            with open(self.file_path, 'w') as f:
                f.writelines(lines)

    def main(self):
        valid_proxies = []  
        invalid_count = 0
        if self.file_path:
            with open(self.file_path, 'r') as file:
                proxies = file.read().splitlines()

            with ThreadPoolExecutor(max_workers=10) as executor:
                results = executor.map(self.check_proxy, proxies)

            for result in results:
                if result:
                    valid_proxies.append(result) 
                else:
                    invalid_count += 1

            self.remove_duplicates()

            with open("done.txt", 'w') as f:
                for proxy in valid_proxies:
                    f.write(proxy + '\n')

            print(">> Done check")

            with open("done.txt", 'r') as file:
                valid_proxies = file.read().splitlines()

            invalid_proxies = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = executor.map(self.check_proxy, valid_proxies)

            for result in results:
                if not result:
                    invalid_proxies.append(result)

            if invalid_proxies:
                with open("done.txt", 'w') as f:
                    for proxy in valid_proxies:
                        if proxy not in invalid_proxies:
                            f.write(proxy + '\n')

                print("Удалены невалидные прокси из done.txt")

    def check_proxies(self):
        if self.file_path:
            self.main()
        else:
            print("Выберите файл с прокси")

def main():
    if len(sys.argv) != 2:
        print("Использование: python proxy_checker.py <путь_к_файлу_с_прокси>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    proxy_checker = ProxyChecker(file_path)
    proxy_checker.check_proxies()

if __name__ == "__main__":
    main()
