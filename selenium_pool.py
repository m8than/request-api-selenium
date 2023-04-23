import time
from selenium import webdriver
import threading


class SeleniumPool:
    def __init__(self, pool_size):
        self.pool_size = pool_size
        self.pool = []
        for i in range(pool_size):
            self.pool.append(self.create_instance())
            
        # start worker thread to reset pool every 5 minutes
        threading.Thread(target=self.worker_thread).start()
        
    def create_instance(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized") # open Browser in maximized mode
        options.add_argument("disable-infobars") # disabling infobars
        options.add_argument("--disable-extensions") # disabling extensions
        options.add_argument("--disable-gpu") # applicable to windows os only
        options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
        options.add_argument("--no-sandbox") # Bypass OS security model
        # headless
        options.add_argument("--headless")
        # set user agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        
        driver.in_use = False # add in_use flag
        return driver
    
    def get_instance(self):
        while True:
            for instance in self.pool:
                if not instance.in_use:
                    instance.in_use = True
                    return instance
            time.sleep(1)
    
    def release_instance(self, instance):
        instance.in_use = False
        
    def destroy_pool(self):
        for instance in self.pool:
            while instance.in_use:
                time.sleep(1)
            instance.quit()
        self.pool = []
        
    def repair_pool(self):
        for instance in self.pool:
            try:
                instance.title # check if instance is still usable
            except:
                self.pool.remove(instance)
                instance.quit()
                new_instance = self.create_instance()
                self.pool.append(new_instance)

    def reset_pool(self):
        self.destroy_pool()
        for i in range(self.pool_size):
            self.pool.append(self.create_instance())
            
    def worker_thread(self):
        pool_reset = time.time()
        pool_repair = time.time()
        while True:
            if time.time() - pool_reset > 300:
                self.reset_pool()
                pool_reset = time.time()
                
            if time.time() - pool_repair > 60:
                self.repair_pool()
                pool_repair = time.time()
                
            time.sleep(1)
            