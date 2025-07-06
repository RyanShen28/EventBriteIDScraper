import json
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightException

ConcurrentQueries = 10
eventText = {}
emptyFlag = False
#fetch scrapes the IDs from the page
async def fetch(browser, url, idNo, results):
    global emptyFlag
    try:
        full_url = url + str(idNo)
        page = await browser.new_page()
        try:
            await page.goto(full_url, wait_until="domcontentloaded", timeout = 12000)

            div = await page.wait_for_selector('div.eds-text--left', timeout = 12000)


            if div == None:
                print(f"Page {idNo} is empty")
                emptyFlag = True  # signals end
            paragraphs = await div.query_selector_all('p')
            page_text = ''
            for p in paragraphs:
                text = await p.text_content()
                if text:
                    page_text += text.strip() + '\n'
            eventText.update({idNo: page_text})
            print(idNo+" updated")
        except PlaywrightException:
            print("Timed out / No data")
            eventText.update({idNo: ""})
        await page.close()

    except Exception as e:
        print(f"Error on id {idNo}: {e}")
        emptyFlag = True
        await page.close()

async def worker(browser, url, queue, results):
    while not emptyFlag:
        try:
            idNo = queue.get_nowait()
        except asyncio.QueueEmpty:
            #only happens when queue runs out of pages, which should rarely happen
            break

        await fetch(browser, url, idNo, results)

async def scrape(url):
    global emptyFlag
    results = []

    queue = asyncio.Queue()
    #add all page numbers to the queue
    with open("eventIDs_chicago.txt", "r") as file:
        for i in file.readlines():
            i = i.strip()
            queue.put_nowait(i)



    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        #creates ConcurrentQueries workers, that run fetch
        workers = [
            asyncio.create_task(worker(browser, url, queue, results))
            for _ in range(ConcurrentQueries)
        ]
        await asyncio.gather(*workers)

        await browser.close()
    #writes IDs to .txt
    with open("event_page_text_chicago.ndjson", "w") as jsonfile:
        json.dump(eventText, jsonfile, indent = 4)


async def main():
    url = "http://eventbrite.com/e/"
    await scrape(url)

if __name__ == "__main__":
    asyncio.run(main())