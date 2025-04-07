import pandas as pd
import asyncio

from dotenv import load_dotenv

from LLM_Scraper_Summary_Papers import models, ArticleInfo
from LLM_Scraper_Summary_Papers.WebScrapeUtils import get_link_from_search, get_list_content_from_links, do_llm_scrape, \
    get_list_links, get_list_content

load_dotenv()

import streamlit as st
async def get_data(query):
    yearStart = 2025
    search = f"https://scholar.google.com/scholar?as_ylo={yearStart}&q={query}&hl=en&as_sdt=0,5"
    # content = get_content_from_scholar(search)
    links = await get_link_from_search(search)
    contents = await (get_list_content_from_links(links))

    LIMIT_RESULTS = 9
    contents_from_links = contents[0:LIMIT_RESULTS]
    llm = models.getllm()
    article_scrapper_llm = llm.with_structured_output(ArticleInfo.ArticleInfo)
    df = await get_dataframe_from_content(contents_from_links, article_scrapper_llm)
    return df


def get_content_from_scholar(search_string):
    links = get_list_links(search_string)
    contents_from_links = get_list_content(links)
    return contents_from_links


async def get_dataframe_from_content(contents_from_links, article_scrapper_llm):

    tasks = [asyncio.create_task(do_llm_scrape(contemt, article_scrapper_llm)) for contemt in contents_from_links]
    new_items = await asyncio.gather(*tasks)
    # tasks =
    #
    rows = []
    for content in new_items:
        try:
            # extraction, link = do_llm_scrape(content, article_scrapper_llm)
            extraction, link = content
            row = extraction.__dict__
            row["url"] = link
            rows.append(row)
        except:
            continue
    projects_df = pd.DataFrame(rows)
    return projects_df


st.title("Google Scholar Article Helper")
st.write("Get all results from 1st page of results, analize the articles and print the highlights in a dataframe")
st.write("If one article's summary seemns interesting just click the link next to it")

query = st.text_input("enter the search query that will be passed to google scholar")
loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(loop)
if len(query) > 1:
    df=loop.run_until_complete(get_data(query))
    st.dataframe(df, hide_index=True)



