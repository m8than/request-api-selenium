from concurrent.futures import ThreadPoolExecutor
import re
import time
from selenium_pool import SeleniumPool
import atexit
import asyncio
from aiohttp import web
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pool = SeleniumPool(5)

executor = ThreadPoolExecutor()

loader_selectors = [
    '[class*="loader"]',
    '[id*="loader"]',
    '[class*="loading"]',
    '[id*="loading"]',
    '[class*="spinner"]',
    '[id*="spinner"]',
    '[class*="progress"]',
    '[id*="progress"]',
]

async def index(request):
    args = request.query
    
    if 'url' not in args:
        return web.Response(text='No url provided')
    
    instance = pool.get_instance()
    instance.get(args['url'])
    
    # wait for page to load
    while instance.execute_script('return document.readyState') != 'complete':
        await asyncio.sleep(0.01)
        
    # wait for loading icon to disappear
    wait = WebDriverWait(instance, 10)
    
    try:
        loading_icon = await asyncio.get_event_loop().run_in_executor(executor, wait.until, EC.invisibility_of_element_located((By.CSS_SELECTOR, ','.join(loader_selectors))))
    except:
        return web.Response(text='Timed out (10 seconds) waiting for loading icon to disappear')
    
    # reset instance cookies and local storage
    instance.delete_all_cookies()
    instance.execute_script('window.localStorage.clear();')
    pool.release_instance(instance)
        
    return web.Response(content_type='text/html', text=instance.page_source)

def cleanup():
    pool.destroy_pool()

if __name__ == '__main__':
    # register event to kill all selenium instances on exit
    atexit.register(cleanup)

    app = web.Application()
    app.add_routes([web.get('/', index)])
    web.run_app(app, port=8080)