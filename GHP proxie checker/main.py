import requests
import socket
import socks
from concurrent.futures import ThreadPoolExecutor
import time
import os
import sys
from argparse import ArgumentParser
from time import sleep

class GHProxyChecker:
    def __init__(self):
        self.timeout = 10
        self.test_urls = [
            "http://www.google.com",
            "http://www.example.com",
            "https://www.github.com"
        ]
        self.working_proxies = []
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.current_file = ""
        self.max_threads = 50

    def display_logo(self):
        logo = r"""

░██████╗░██╗░░██╗██████╗░  ██████╗░██████╗░░█████╗░██╗░░██╗██╗███████╗
██╔════╝░██║░░██║██╔══██╗  ██╔══██╗██╔══██╗██╔══██╗╚██╗██╔╝██║██╔════╝
██║░░██╗░███████║██████╔╝  ██████╔╝██████╔╝██║░░██║░╚███╔╝░██║█████╗░░
██║░░╚██╗██╔══██║██╔═══╝░  ██╔═══╝░██╔══██╗██║░░██║░██╔██╗░██║██╔══╝░░
╚██████╔╝██║░░██║██║░░░░░  ██║░░░░░██║░░██║╚█████╔╝██╔╝╚██╗██║███████╗
░╚═════╝░╚═╝░░╚═╝╚═╝░░░░░  ╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚═╝╚══════╝
        """
        print("\033[1;36m" + logo + "\033[0m")
        print("\033[1;34m" + " " * 15 + "Advanced Proxy Checker v2.0" + "\033[0m")
        print("\n")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self):
        self.clear_screen()
        self.display_logo()
        print(" " * 10 + "\033[1;37mMain Menu\033[0m")
        print("=" * 40)
        print("1. Load Proxy File")
        print("2. Set Thread Count (Current: {})".format(self.max_threads))
        print("3. Check Proxies")
        print("4. View Results")
        print("5. Save Results")
        print("6. Exit")
        print("=" * 40)
        if self.current_file:
            print(f"\nCurrent File: \033[1;32m{self.current_file}\033[0m")
            print(f"Loaded Proxies: \033[1;33m{len(self.load_proxies(self.current_file)) if os.path.exists(self.current_file) else 0}\033[0m")
        print("\n")

    def get_user_choice(self):
        while True:
            try:
                choice = int(input("\033[1;35mEnter your choice (1-6): \033[0m"))
                if 1 <= choice <= 6:
                    return choice
                else:
                    print("\033[1;31mInvalid choice. Please enter a number between 1 and 6.\033[0m")
            except ValueError:
                print("\033[1;31mInvalid input. Please enter a number.\033[0m")

    def load_proxy_file(self):
        self.clear_screen()
        self.display_logo()
        print("\033[1;37mLoad Proxy File\033[0m")
        print("=" * 40)
        file_path = input("\nEnter path to proxy file: ").strip()
        
        if not os.path.exists(file_path):
            print("\033[1;31mError: File not found!\033[0m")
            sleep(2)
            return
        
        self.current_file = file_path
        proxy_count = len(self.load_proxies(file_path))
        print(f"\n\033[1;32mSuccessfully loaded {proxy_count} proxies from {file_path}\033[0m")
        sleep(2)

    def set_thread_count(self):
        self.clear_screen()
        self.display_logo()
        print("\033[1;37mSet Thread Count\033[0m")
        print("=" * 40)
        print(f"\nCurrent thread count: \033[1;33m{self.max_threads}\033[0m")
        
        while True:
            try:
                threads = int(input("\nEnter new thread count (1-200): "))
                if 1 <= threads <= 200:
                    self.max_threads = threads
                    print(f"\033[1;32mThread count set to {threads}\033[0m")
                    sleep(1.5)
                    return
                else:
                    print("\033[1;31mPlease enter a value between 1 and 200\033[0m")
            except ValueError:
                print("\033[1;31mInvalid input. Please enter a number.\033[0m")

    def check_proxies(self):
        if not self.current_file:
            print("\033[1;31mNo proxy file loaded!\033[0m")
            sleep(2)
            return
        
        proxies = self.load_proxies(self.current_file)
        if not proxies:
            print("\033[1;31mNo proxies to check!\033[0m")
            sleep(2)
            return
        
        self.clear_screen()
        self.display_logo()
        print("\033[1;37mChecking Proxies\033[0m")
        print("=" * 40)
        print(f"\nProxies to check: \033[1;33m{len(proxies)}\033[0m")
        print(f"Threads: \033[1;33m{self.max_threads}\033[0m")
        print("\nStarting check... (This may take some time)")
        
        start_time = time.time()
        self.working_proxies = self.check_proxy_list(proxies, self.max_threads)
        elapsed = time.time() - start_time
        
        print("\n\033[1;32mCheck completed!\033[0m")
        print(f"Working proxies: \033[1;32m{len(self.working_proxies)}\033[0m")
        print(f"Success rate: \033[1;33m{len(self.working_proxies)/len(proxies)*100:.1f}%\033[0m")
        print(f"Time taken: \033[1;33m{elapsed:.2f} seconds\033[0m")
        input("\nPress Enter to return to menu...")

    def view_results(self):
        if not self.working_proxies:
            print("\033[1;31mNo results to display!\033[0m")
            sleep(2)
            return
        
        self.clear_screen()
        self.display_logo()
        print("\033[1;37mProxy Check Results\033[0m")
        print("=" * 40)
        print(f"\nTotal working proxies: \033[1;32m{len(self.working_proxies)}\033[0m\n")
        
        print("\033[1;37m{:<20} {:<8} {:<10} {:<12} {:<15}\033[0m".format(
            "Proxy", "Type", "Latency", "Anonymity", "Country"))
        print("-" * 70)
        
        for proxy in self.working_proxies[:50]:  # Show first 50 to avoid overflow
            print("{:<20} {:<8} {:<10} {:<12} {:<15}".format(
                proxy['proxy'],
                proxy['type'],
                f"{proxy['latency']}ms" if proxy['latency'] else "N/A",
                proxy['anonymity'],
                proxy['country']
            ))
        
        if len(self.working_proxies) > 50:
            print(f"\n\033[1;33m(Showing 50 of {len(self.working_proxies)} results. Save to file to see all.)\033[0m")
        
        input("\nPress Enter to return to menu...")

    def save_results(self):
        if not self.working_proxies:
            print("\033[1;31mNo results to save!\033[0m")
            sleep(2)
            return
        
        self.clear_screen()
        self.display_logo()
        print("\033[1;37mSave Results\033[0m")
        print("=" * 40)
        
        default_file = "working_proxies.txt"
        save_path = input(f"\nEnter output file path (default: {default_file}): ").strip() or default_file
        
        try:
            with open(save_path, 'w') as f:
                f.write("Proxy | Type | Latency | Anonymity | Country\n")
                f.write("-" * 50 + "\n")
                for proxy in self.working_proxies:
                    f.write(f"{proxy['proxy']} | {proxy['type']} | {proxy['latency']}ms | {proxy['anonymity']} | {proxy['country']}\n")
            
            print(f"\n\033[1;32mResults saved to {save_path}\033[0m")
            sleep(2)
        except Exception as e:
            print(f"\n\033[1;31mError saving file: {e}\033[0m")
            sleep(2)

    # Core proxy checking functions (same as before)
    def load_proxies(self, file_path):
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines() if line.strip()]
        
        return proxies

    def check_proxy(self, proxy):
        proxy = proxy.strip()
        if not proxy:
            return None
        
        proxy_types = [
            ('http', self.check_http_proxy),
            ('socks4', self.check_socks_proxy),
            ('socks5', self.check_socks_proxy)
        ]
        
        for proxy_type, check_func in proxy_types:
            if check_func(proxy, proxy_type):
                result = {
                    'proxy': proxy,
                    'type': proxy_type,
                    'latency': self.measure_latency(proxy, proxy_type),
                    'anonymity': self.check_anonymity(proxy, proxy_type),
                    'country': self.get_country(proxy, proxy_type)
                }
                return result
        return None

    def check_http_proxy(self, proxy, proxy_type):
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get(
                self.test_urls[0],
                proxies=proxies,
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent}
            )
            return response.status_code == 200
        except:
            return False

    def check_socks_proxy(self, proxy, proxy_type):
        try:
            host, port = proxy.split(':')
            port = int(port)
            
            socks.set_default_proxy(
                socks.SOCKS4 if proxy_type == 'socks4' else socks.SOCKS5,
                host,
                port
            )
            socket.socket = socks.socksocket
            
            response = requests.get(
                self.test_urls[0],
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent}
            )
            
            socks.set_default_proxy()
            socket.socket = socket._socketobject
            
            return response.status_code == 200
        except:
            socks.set_default_proxy()
            socket.socket = socket._socketobject
            return False

    def measure_latency(self, proxy, proxy_type):
        try:
            start_time = time.time()
            if proxy_type in ['http', 'https']:
                proxies = {
                    'http': f'{proxy_type}://{proxy}',
                    'https': f'{proxy_type}://{proxy}'
                }
                requests.get(
                    self.test_urls[0],
                    proxies=proxies,
                    timeout=self.timeout,
                    headers={'User-Agent': self.user_agent}
                )
            else:
                host, port = proxy.split(':')
                port = int(port)
                socks.set_default_proxy(
                    socks.SOCKS4 if proxy_type == 'socks4' else socks.SOCKS5,
                    host,
                    port
                )
                socket.socket = socks.socksocket
                requests.get(
                    self.test_urls[0],
                    timeout=self.timeout,
                    headers={'User-Agent': self.user_agent}
                )
                socks.set_default_proxy()
                socket.socket = socket._socketobject
            
            return round((time.time() - start_time) * 1000, 2)
        except:
            return None

    def check_anonymity(self, proxy, proxy_type):
        try:
            test_url = "http://httpbin.org/ip"
            if proxy_type in ['http', 'https']:
                proxies = {
                    'http': f'{proxy_type}://{proxy}',
                    'https': f'{proxy_type}://{proxy}'
                }
                response = requests.get(
                    test_url,
                    proxies=proxies,
                    timeout=self.timeout,
                    headers={'User-Agent': self.user_agent}
                )
            else:
                host, port = proxy.split(':')
                port = int(port)
                socks.set_default_proxy(
                    socks.SOCKS4 if proxy_type == 'socks4' else socks.SOCKS5,
                    host,
                    port
                )
                socket.socket = socks.socksocket
                response = requests.get(
                    test_url,
                    timeout=self.timeout,
                    headers={'User-Agent': self.user_agent}
                )
                socks.set_default_proxy()
                socket.socket = socket._socketobject
            
            if "origin" in response.json():
                return "Anonymous" if "," not in response.json()["origin"] else "Transparent"
            return "Unknown"
        except:
            return "Unknown"

    def get_country(self, proxy, proxy_type):
        try:
            ip = proxy.split(':')[0]
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=self.timeout)
            data = response.json()
            return data.get('country', 'Unknown') if data.get('status') == 'success' else 'Unknown'
        except:
            return "Unknown"

    def check_proxy_list(self, proxy_list, max_workers=50):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.check_proxy, proxy_list))
        
        return [result for result in results if result is not None]

    def run(self):
        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == 1:
                self.load_proxy_file()
            elif choice == 2:
                self.set_thread_count()
            elif choice == 3:
                self.check_proxies()
            elif choice == 4:
                self.view_results()
            elif choice == 5:
                self.save_results()
            elif choice == 6:
                print("\n\033[1;36mThank you for using GHP Proxy Checker. Goodbye!\033[0m")
                sys.exit(0)

if __name__ == "__main__":
    checker = GHProxyChecker()
    checker.run()