import asyncio
import re

import html2text
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from LLM_Scraper_Summary_Papers.models import SYSTEM_PROMPT, create_scrape_prompt


def findURL(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


async def extract_content_from_link(playwright, link, semaphore):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    try:
        async with semaphore:
            browser = await playwright.chromium.launch(headless=False, slow_mo=1000)

            context = await browser.new_context(user_agent=USER_AGENT)

            page = await context.new_page()
            await page.goto(link)
            content = await page.content()

            markdown_converter = html2text.HTML2Text()
            markdown_converter.ignore_links = False
            markdown_content = markdown_converter.handle(content)
            is_article = len(markdown_content) > 2000;
            is_scientific = "abstract" in markdown_content.lower()
            # if not_article and not_scientific:
            #
            #         locator = page.get_by_role("button", name="accept")
            #         locator.hover()
            #         locator.click()
            await browser.close()
            if is_article and is_scientific:
                return markdown_content, link
    except Exception as e: print(e)


def get_list_links(search_string):
    links = asyncio.run(get_link_from_search(search_string))
    return links


async def get_link_from_search(search_string):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=500)

    context = await browser.new_context(user_agent=USER_AGENT)

    page = await context.new_page()
    await page.goto(search_string)
    # await page.screenshot(path="scren.png",full_page=True)
    content = await page.content()
    await browser.close()
    await playwright.stop()
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(content)
    # print(markdown_content)
    links = findURL(markdown_content)
    filtered_for_google = list(filter(lambda x: not "google" in x, links))
    return links


def get_list_content(links):
    list_content = asyncio.run(get_list_content_from_links(links))
    return list_content


async def get_list_content_from_links(links):

    playwright = await async_playwright().start()
    # Async see later, error in playwrite
    s = asyncio.Semaphore(value=3)
    tasks = [asyncio.create_task(extract_content_from_link(playwright, link, s)) for link in links]
    results = await asyncio.gather(*tasks)
    list_content = filter(lambda x:x is not None,results)
    await playwright.stop()
    return list(list_content)


async def do_llm_scrape(content, article_scrapper_llm):
    text = content[0][:10000]
    link = content[1]
    extraction = article_scrapper_llm.invoke(
        [("system", SYSTEM_PROMPT), ("user", create_scrape_prompt(text))]
    )

    return extraction, link
