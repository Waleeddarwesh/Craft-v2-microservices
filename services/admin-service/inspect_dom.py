import os, time
from playwright.sync_api import sync_playwright

def inspect_swagger():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://127.0.0.1:8000/developer/explorer/')
        
        # login if redirected
        if 'login' in page.url:
            page.fill('input[name="username"]', 'walid')
            page.fill('input[name="password"]', 'walid')
            page.click('button[type="submit"]')
            page.wait_for_url('http://127.0.0.1:8000/developer/explorer/')
        
        # Wait a moment for Swagger to render
        time.sleep(3)
        
        script = """
        () => {
            let els = document.querySelectorAll('*');
            let results = [];
            for(let el of els) {
                let rect = el.getBoundingClientRect();
                if(rect.height > 500 && el.id !== 'swagger-scroll-container') {
                    let style = window.getComputedStyle(el);
                    let mt = parseInt(style.marginTop) || 0;
                    let pt = parseInt(style.paddingTop) || 0;
                    if (mt > 100 || pt > 100 || rect.height > 1000) {
                        results.push({
                            tag: el.tagName,
                            id: el.id,
                            class: el.className,
                            height: rect.height,
                            mt: mt,
                            pt: pt
                        });
                    }
                }
            }
            return results;
        }
        """
        res = page.evaluate(script)
        for r in res:
            print(f"Element: <{r['tag']} id='{r['id']}' class='{r['class']}'>, Height: {r['height']}, mt: {r['mt']}, pt: {r['pt']}")
            
        browser.close()

if __name__ == '__main__':
    inspect_swagger()
