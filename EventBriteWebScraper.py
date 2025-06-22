import requests
import csv
import lxml.html as lh
from lxml import etree
import config
#from util.Metric_Imperial_Converter import convert
#from util.Parser import Parser
#from util.Utils import Utils
import asyncio
from playwright.async_api import async_playwright, Playwright, TimeoutError, Error
import json
import re




#currently Chicago only








#todo: fix this
#
# future: <Future finished exception=TargetClosedError('Target page, context or browser has been closed')>
# playwright._impl._errors.TargetClosedError: Target page, context or browser has been closed
# Future exception was never retrieved


#maybe vary sleep time?
# configuration




session = requests.Session()

ConcurrentQueries = 5

max_page = 100

sem = asyncio.Semaphore(ConcurrentQueries)

emptyFlag = False


async def fetch(browser, url, sem, pageNo, results):
   global emptyFlag
   async with sem:
       try:
           url = url+str(pageNo)

           page = await browser.new_page()
           await page.goto(url, wait_until="domcontentloaded", timeout=9000)

           eventcardactions = await page.locator('//section[@class="event-card-actions"]').all()

           if(len(eventcardactions) == 0):
               emptyFlag = True
           else:
               for event in eventcardactions:
                   data_id = await event.get_attribute("data-event-id")
                   results.append(data_id)

               print("Successfully scraped eventbrite page: "+str(pageNo))

           await page.close()
       except TimeoutError:

           print("No data")

           await page.close()
       except Exception as e:
           print(str(e))
           if "net::ERR_NETWORK_CHANGED" in str(e):
               print("Network change detected, retry fetch")
               await page.close()
               await asyncio.sleep(3)
               await fetch(browser, url, sem, pageNo, results)
           else:
               print("Unknown error")
               await page.close()




async def scrape(url):


   #definitions
   session = requests.Session()

   global emptyFlag
   results = []
   counter = 0

   while(counter < max_page and emptyFlag == False):
       async with async_playwright() as p:
           browser = await p.chromium.launch(headless=True)
           try:
               tasks = [fetch(browser, url, sem, pageNo, results) for pageNo in list(range(counter, counter+ConcurrentQueries+1))]
               await asyncio.gather(*tasks, return_exceptions=True)
           finally:
               await browser.close()
       counter += ConcurrentQueries




   with open("eventIDs_chicago.txt", "w") as file:
       for i in results:
           file.write(i+"\n")












async def main():
   url = 'http://eventbrite.com/d/il--chicago/all-events/?page='
   await scrape(url)




if __name__ == "__main__":
   asyncio.run(main())









