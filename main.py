
import os
import sys
import time

from dotenv import load_dotenv
from playwright.sync_api import Page, TimeoutError, sync_playwright
# from playwright_stealth import stealth_sync


def bell():
    print('bell')
    sys.stdout.write('\a')
    sys.stdout.flush()


def cap_and_wait(page: Page):
    page.screenshot(path=f"./screenshots/screenshot-{int(time.time())}.png")
    time.sleep(3.0)


def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.3+
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)


def three_bell():
    for i in range(3):
        if i:
            time.sleep(1)

        bell()


def trill():
    print('---trill---')
    for _ in range(10):
        sys.stdout.write('\a')
        sys.stdout.flush()
        time.sleep(0.5)

def main():
    load_dotenv(override=True)
    with sync_playwright() as sync:
        # Channel can be "chrome", "msedge", "chrome-beta", "msedge-beta" or "msedge-dev".
        browser = sync.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()
        # stealth_sync(page)

        page.goto(os.environ['URL'], wait_until="load")
        cap_and_wait(page)


        page.locator('#my-login-button').locator('a').click()
        page.wait_for_load_state("load")
        cap_and_wait(page)


        page.locator('#Email').fill(os.environ['USERNAME'])
        page.locator('#Password').fill(os.environ['PASSWORD'])
        page.locator('#login-button').click()
        page.wait_for_load_state("load")
        cap_and_wait(page)
        

        # Expand the section
        page.get_by_text('Courses - Active').click()

        new_page = None
        with context.expect_page() as new_page:
            el = page.get_by_text('RESUME')
            el.click()
        

        if new_page:
            new_page = new_page.value
            new_page.wait_for_load_state("load")
            cap_and_wait(new_page)

            while True:
                next_button = new_page.locator('div.button-next').all()
                timer_div = new_page.locator('div.arrow-next-locked').locator('nth=1').all()
                if timer_div and timer_div[0].is_visible:
                    print(f"timer text={timer_div[0].text_content().strip()}")
                    timer = timer_div[0].text_content().strip()
                    if timer:
                        if ':' in timer:
                            min, sec = timer.split(':')
                            sec = (int(min)*60) + int(sec) + 1
                        else:
                            sec = int(timer) + 1

                        print(f"{sec=}")
                        for _ in progressbar(range(sec-3), f"{sec}s countdown", 60):
                            time.sleep(1) # any code you need

                        bell()
                    else:
                        three_bell()
                        for _ in range(3):
                            try:
                                timer_div = new_page.locator('div.arrow-next-locked').locator('nth=1')
                                break
                            except TimeoutError:
                                print("Waiting for lock timer...")

                elif next_button and not next_button[0].get_attribute('hidden'):
                    print(next_button[0].get_attribute('hidden'))
                    print("next button is enabled")
                    next_button[0].click()
                    new_page.wait_for_load_state("load")
                    cap_and_wait(new_page)

                else:
                    print('neither')

        browser.close()

        '''
        div.button-next hidden-xs
            i.fa fa-chevron-right fa-5x

        div.arrow-next-locked hidden-xs
            i.fa fa-lock fa-5x

        <modal-container class="modal fade in" role="dialog" tabindex="-1" style="display: block;">
            <div role="document" class="modal-dialog modal-lg">
            <div class="modal-content">
        <div _ngcontent-c6="" class="modal-header">
            <h4 _ngcontent-c6="" class="modal-title pull-left">Are you still there?</h4>
        </div>
        <div _ngcontent-c6="" class="modal-body">
            <div _ngcontent-c6="" class="alert alert-info">
            <span _ngcontent-c6="">You have been inactive and will be logged out in 1:33 minutes.</span>
            </div>
            <button _ngcontent-c6="" class="btn">Log Out Now</button>    
            <button _ngcontent-c6="" class="btn btn-primary pull-right">Continue Course</button>    
        </div>
        </div>
            </div>
        </modal-container>
        '''
if __name__ == '__main__':
    main()
