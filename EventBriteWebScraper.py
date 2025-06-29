import asyncio
from playwright.async_api import async_playwright

ConcurrentQueries = 15
max_page = 100 #generally goes up to only 50 or so for large cities

emptyFlag = False
#fetch scrapes the IDs from the page
async def fetch(browser, url, pageNo, results):
    global emptyFlag
    try:
        full_url = url + str(pageNo)
        page = await browser.new_page()
        await page.goto(full_url, wait_until="domcontentloaded", timeout = 35000)

        eventcardactions = await page.locator('//section[@class="event-card-actions"]').all()
        #eventbrite events on the main search page are most easily defined by their event-card-actions class found using locator

        if len(eventcardactions) == 0:
            print(f"Page {pageNo} is empty")
            emptyFlag = True  # signals end
        else:
            #events on page found
            for event in eventcardactions:
                data_id = await event.get_attribute("data-event-id")
                results.append(data_id)

            print(f"Scraped page {pageNo}")

        await page.close()

    except Exception as e:
        print(f"Error on page {pageNo}: {e}")
        await page.close()

async def worker(browser, url, queue, results):
    while not emptyFlag:
        try:
            pageNo = queue.get_nowait()
        except asyncio.QueueEmpty:
            #only happens when queue runs out of pages, which should rarely happen
            break

        await fetch(browser, url, pageNo, results)

async def scrape(url):
    global emptyFlag
    results = []

    queue = asyncio.Queue()
    #add all page numbers to the queue
    for pageNo in range(1, max_page + 1):
        queue.put_nowait(pageNo)


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
    with open("eventIDs_chicago.txt", "a") as file:
        for i in results:
            file.write(i + "\n")

async def main():
    url = "http://eventbrite.com/d/il--chicago/all-events/?page="
    #change il and chicago as needed
    await scrape(url)

if __name__ == "__main__":
    asyncio.run(main())