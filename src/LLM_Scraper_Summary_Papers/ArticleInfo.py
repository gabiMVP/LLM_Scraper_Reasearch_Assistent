from pydantic import BaseModel, Field
from typing import List, Optional


# class Referece(BaseModel):
#     """a reference found in the article , these are usually found in the lower part and always has a link poiting to the article"""
#     title_of_referenced:Optional[str] = Field("Reference of the article e.g WHO Global tuberculosis report (2023)")
#     url:Optional[str] = Field("Link mentioned  e.g https://www.who.int/teams/global-tuberculosis-programme/tb-reports/global-tuberculosis-report-2023")


class ArticleInfo(BaseModel):
    """Information about the article"""

    Title: Optional[str] =Field("title of article e.g. New way to treat disease ")
    Methods: Optional[str] = Field("Summary of the methods used of the article ")
    Results: Optional[str] = Field("Summary of the results of the article ")
    Conclusions :Optional[str] = Field("Summary of the Conclusions of the article ")
    # References :Optional[List[Referece]] = Field("Reference the article makes to another article ")


