import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from config import BOT_TOKEN, CHAT_ID

# 여러 User-Agent 문자열을 리스트로 준비
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'
]

# 전역 플래그 설정 (중지 기능 구현)
monitoring = False


# Chrome Options 설정 함수
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # 새로운 헤드리스 모드
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-javascript')
    chrome_options.add_argument('--window-position=-32000,-32000')
    
    # 무작위로 User-Agent 선택
    random_user_agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f'user-agent={random_user_agent}')
    
    return chrome_options

def create_driver():
    service = Service(ChromeDriverManager().install())
    service.creation_flags = 0x08000000  # 콘솔 창 숨기기
    return webdriver.Chrome(service=service, options=get_chrome_options())

def get_movie_info(midx):
    browser = None
    try:
        browser = create_driver()
        url = f'http://www.cgv.co.kr/movies/detail-view/?midx={midx}'
        
        browser.set_page_load_timeout(10)
        browser.implicitly_wait(5)
        browser.get(url)
        
        wait = WebDriverWait(browser, 5)
        
        title = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.box-contents div.title strong"))
        ).text
        
        release_date = wait.until(
            EC.presence_of_element_located((By.XPATH, "//dt[contains(text(), '개봉 :')]/following-sibling::dd[@class='on']"))
        ).text
        
        return title, release_date
    except Exception as e:
        print(f'영화 정보 가져오기 실패: {e}')
        return "정보 불러오기 실패", "정보 불러오기 실패"
    finally:
        if browser:
            browser.quit()

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
        return True
    except Exception as e:
        print('텔레그램 메시지 전송 실패:', e)
        return False

def check_reservation(midx, interval, app):
    global monitoring
    browser = None
    try:
        browser = create_driver()
        url = f'http://www.cgv.co.kr/movies/detail-view/?midx={midx}'
        
        while monitoring:
            print(f'{url} 페이지 접속 중...')
            browser.get(url)
            
            try:
                wait = WebDriverWait(browser, 5)
                reservation_button = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'link-reservation'))
                )
                if reservation_button:
                    reservation_url = reservation_button.get_attribute('href')
                    message = f"예약 가능: {reservation_url}"
                    print(message)
                    send_telegram_message(message)
                    app.update_status(f"예매 버튼이 발견되었습니다: {reservation_url}", "green")
                    break
            except:
                app.update_status(f'예약 버튼이 없습니다. {interval}분 후 다시 시도합니다.', "red")
            
            for i in range(interval):
                if not monitoring:
                    break
                app.update_next_check(f'{interval - i}분 후 다시 시도합니다...')
                time.sleep(60)
    except Exception as e:
        print(f'에러 발생: {e}')
    finally:
        if browser:
            browser.quit()

class MovieMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CGV 예매 모니터링")
        
        # MIDX 입력 프레임
        midx_frame = tk.Frame(root)
        midx_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(midx_frame, text="midx 값:").pack(side=tk.LEFT)
        self.entry_midx = tk.Entry(midx_frame)
        self.entry_midx.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 5))
        
        check_button = tk.Button(midx_frame, text="체크", command=self.check_movie_info)
        check_button.pack(side=tk.RIGHT)
        
        # 상태 표시 레이블
        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack(padx=10, pady=(0, 5))

        # 영화 정보 프레임
        info_frame = tk.Frame(root)
        info_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(info_frame, text="영화 제목:").grid(row=0, column=0, sticky=tk.W)
        self.label_title_value = tk.Label(info_frame, text="N/A", wraplength=200)
        self.label_title_value.grid(row=0, column=1, sticky=tk.W)
        
        tk.Label(info_frame, text="개봉일:").grid(row=1, column=0, sticky=tk.W)
        self.label_release_value = tk.Label(info_frame, text="N/A")
        self.label_release_value.grid(row=1, column=1, sticky=tk.W)

        # 간격 설정 프레임
        interval_frame = tk.Frame(root)
        interval_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(interval_frame, text="확인 간격(분):").pack(side=tk.LEFT)
        self.entry_interval = tk.Entry(interval_frame)
        self.entry_interval.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # 버튼 프레임
        button_frame = tk.Frame(root)
        button_frame.pack(padx=10, pady=10)
        
        tk.Button(button_frame, text="모니터링 시작", command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="모니터링 중지", command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="텔레그램 테스트", command=self.test_telegram).pack(side=tk.LEFT, padx=5)

        # 다음 체크 시간 표시 레이블
        self.next_check_label = tk.Label(root, text="", fg="blue")
        self.next_check_label.pack(padx=10, pady=(0, 5))

    def check_movie_info(self):
        midx = self.entry_midx.get()
        if not midx:
            messagebox.showerror("입력 오류", "midx 값을 입력해주세요.")
            return
        
        self.update_status("정보 확인 중...", "blue")
        self.label_title_value.config(text="확인 중...")
        self.label_release_value.config(text="확인 중...")
        
        def check():
            title, release_date = get_movie_info(midx)
            self.label_title_value.config(text=title)
            self.label_release_value.config(text=release_date)
            self.update_status("정보 확인 완료", "green")
            self.root.after(3000, lambda: self.update_status(""))
        
        threading.Thread(target=check, daemon=True).start()

    def start_monitoring(self):
        global monitoring
        midx = self.entry_midx.get()
        interval = self.entry_interval.get()
        
        if not midx or not interval:
            messagebox.showerror("입력 오류", "모든 입력값을 입력해주세요.")
            return
        
        try:
            interval = int(interval)
        except ValueError:
            messagebox.showerror("입력 오류", "간격은 숫자로 입력해주세요.")
            return
        
        monitoring = True
        self.update_status("모니터링 시작", "green")
        threading.Thread(target=check_reservation, args=(midx, interval, self), daemon=True).start()

    def stop_monitoring(self):
        global monitoring
        monitoring = False
        self.update_status("모니터링 중지됨", "red")

    def test_telegram(self):
        self.update_status("텔레그램 테스트 중...", "blue")
        success = send_telegram_message("테스트 메시지: 텔레그램 전송이 정상적으로 동작합니다.")
        if success:
            self.update_status("텔레그램 전송 성공", "green")
        else:
            self.update_status("텔레그램 전송 실패", "red")
        
        self.root.after(3000, lambda: self.update_status(""))

    def update_status(self, message, color="blue"):
        self.status_label.config(text=message, fg=color)

    def update_next_check(self, message):
        self.next_check_label.config(text=message)

if __name__ == '__main__':
    root = tk.Tk()
    app = MovieMonitorApp(root)
    root.mainloop()
