# -*- coding: utf-8 -*-

# import scrapy
# from scrapy.selector import Selector

# from ..items import PageItem 
# from ..spiders.CustomSpider import CustomSpider


# class CurricunetSpider(CustomSpider):
#     name = "curricunet"
#     allowed_domains = ["curricunet.com"]

#     start_urls = [
#         "http://www.curricunet.com/sac/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/SantaMonica/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/elcamino/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/palomar/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/fresno/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/Coast/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/fullerton/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/canyons/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/RCCD/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/Southwestern/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/sbcc/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/SDCCD/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/mjc/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/kccd/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/msjc/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/moorpark/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/cabrillo/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/AVC/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/cypress/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/chabot/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/SBVC/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/ventura/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/COS/search/course/course_search_result.cfm",
#         "http://www.curricunet.com/butte/search/course/course_search_result.cfm",
#     ]

#     def parse(self, response):
#         rows = response.xpath('td[@class="fld"]/..')
#         for row in rows:
#             links, anchor = row.xpath(".//td")
#             relative_url = result_cell.css("a::attr(href)").extract_first()
#             if not relative_url:
#                 print("no syllabus url found:", result_cell)
#                 # print("relative url", relative_url)
#             relative_url = relative_url.replace("outline_pdf.","outline_html.").replace("outline.","outline_html.")
#             url = response.urljoin(relative_url)
#             # print("url", url)
#             anchor = self.clean_whitespace(row.css("td::text").extract_first() or "")
#             yield scrapy.Request(
#                 url,
#                 meta={
#                     'source_url': response.url,
#                     'source_anchor': anchor,
#                     'depth': response.meta['depth'] + 1,
#                     'hops_from_seed': response.meta['hops_from_seed'] + 1,
#                 },
#                 callback=self.parse_syllabus
#             )
#             break

#     def parse_syllabus(self, response):
#         print(response.url)
#         yield PageItem(
#             url=response.url,
#             content=response.body,
#             headers=response.headers,
#             status=response.status,
#             source_url=response.meta.get('source_url'),
#             source_anchor=response.meta.get('source_anchor'),
#             depth=response.meta.get('depth'),
#             hops_from_seed=response.meta.get('hops_from_seed')
#         )

#     def clean_whitespace(self, s):
#         return re.sub(r"\s+", " ", s).strip()

# http://www.curricunet.com/sac/search/course/
# http://www.curricunet.com/SantaMonica/search/course/
# http://www.curricunet.com/elcamino/search/course/
# http://www.curricunet.com/palomar/search/course/
# http://www.curricunet.com/fresno/search/course/
# http://www.curricunet.com/Coast/search/course/
# http://www.curricunet.com/fullerton/search/course/
# http://www.curricunet.com/canyons/search/course/
# http://www.curricunet.com/RCCD/search/course/
# http://www.curricunet.com/Southwestern/search/course/
# http://www.curricunet.com/sbcc/search/course/
# http://www.curricunet.com/SDCCD/search/course/
# http://www.curricunet.com/mjc/search/course/
# http://www.curricunet.com/kccd/search/course/
# http://www.curricunet.com/msjc/search/course/
# http://www.curricunet.com/moorpark/search/course/
# http://www.curricunet.com/cabrillo/search/course/
# http://www.curricunet.com/AVC/search/course/
# http://www.curricunet.com/cypress/search/course/
# http://www.curricunet.com/chabot/search/course/
# http://www.curricunet.com/SBVC/search/course/
# http://www.curricunet.com/ventura/search/course/
# http://www.curricunet.com/COS/search/course/
# http://www.curricunet.com/butte/search/course/

# http://www.curricunet.com/sccc/search/course/
# http://www.curricunet.com/CITRUS/search/course/
# http://www.curricunet.com/victorvalley/search/course/
# http://www.curricunet.com/westvalley/search/course/
# http://www.curricunet.com/cuesta/search/course/
# http://www.curricunet.com/solano/search/course/
# http://www.curricunet.com/ohlone/search/course/
# http://www.curricunet.com/Coast/search/course/
# http://www.curricunet.com/mission/search/course/
# http://www.curricunet.com/Hartnell/search/course/
# http://www.curricunet.com/merced/search/course/
# http://www.curricunet.com/COD/search/course/
# http://www.curricunet.com/SMCCCD/search/course/
# http://www.curricunet.com/laspositas/search/course/
# http://www.curricunet.com/shasta/search/course/
# http://www.curricunet.com/mpc/search/course/
# http://www.curricunet.com/oxnard/search/course/
# http://www.curricunet.com/yccd/search/course/
# http://www.curricunet.com/napa/search/course/
# http://www.curricunet.com/SMCCCD/search/course/
# http://www.curricunet.com/pccd/search/course/
# http://www.curricunet.com/Crafton/search/course/
# http://www.curricunet.com/Kaskaskia/search/course/
# http://www.curricunet.com/mendocino/search/course/
# http://www.curricunet.com/barstow/search/course/
# http://www.curricunet.com/whatcom/search/course/
# http://www.curricunet.com/columbia/search/course/
# http://www.curricunet.com/siskiyous/search/course/
# http://www.curricunet.com/yccd/search/course/
# http://www.curricunet.com/SMCCCD/search/course/
# http://www.curricunet.com/RCCD/search/course/
# http://www.curricunet.com/saddleback/search/course/
# http://www.curricunet.com/irvine/search/course/

# http://www.evc.edu/home/curricunet
# http://www.sjcc.edu/home/curriculum-course-and-program-outlines
# https://www.butte.edu/curriculum/course_outlines/?area=#course_search_result.cfm
# http://www.tri-c.edu/student-resources/curriculum/
# http://webcms.sierracollege.edu/results.asp
