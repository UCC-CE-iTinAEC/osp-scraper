# # -*- coding: utf-8 -*-

# import scrapy

# from ..spiders.CustomSpider import CustomSpider

# class UHSpider(CustomSpider):
#     name = "uh"
#     allowed_domains = ["uh.edu"]

#     def start_requests(self):
#         terms_url = "https://fp.my.uh.edu/psc/saprd_fp/EMPLOYEE/HRMS/c/UHS_SS_CUSTOM.UHS_HB2504_DISPLAY.GBL?institution_name=UH"
#         subjects_url = "https://fp.my.uh.edu/psc/saprd_fp/EMPLOYEE/HRMS/c/UHS_SS_CUSTOM.UHS_HB2504_DISPLAY.GBL?ICType=Panel&ICElementNum=0&ICStateNum=3&ICResubmit=1&ICAJAX=1&"

#         terms = []
#         subjects = []

#         def get_terms(response):
#         	terms.extend(response.css("#PTSRCHRESULTS td:first-child a::text").extract())
# 	        yield scrapy.Request(subjects_url, callback=get_subjects)

#         def get_subjects(response):
#         	subjects.extend(response.css("#PTSRCHRESULTS td:first-child a::text").extract())
# 	        yield scrapy.Request(subjects_url, callback=get_catalog_numbers)

# 	    def get_catalog_numbers

#         yield scrapy.Request(terms_url, callback=get_terms)

#     def get_file_links(self, response):
#         for tag in response.css('a[title="Syllabus"]'):
#             url = tag.css('a::attr(href)').extract_first()
#             if url:
#                 anchor = tag.css('a::text').extract_first()
#                 yield (url, anchor)
