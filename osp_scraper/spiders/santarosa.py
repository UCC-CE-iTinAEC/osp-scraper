# -*- coding: utf-8 -*-

import scrapy

from ..spiders.CustomSpider import CustomSpider

class SantaRosaSpider(CustomSpider):
    name = "santarosa"

    start_urls = ["https://portal.santarosa.edu/SRWeb/SR_CourseOutlines.aspx"]

    def parse(self, response):
        # Departments list was generated from the courses listed in
        # https://admissions.santarosa.edu/sites/admissions.santarosa.edu/files/Catalog%202016-17%20Section%207.pdf
        departments = ["AG", "AGBUS", "AGMEC", "AGRI", "AJ", "ANAT", "ANHLT", "ANSCI", "ANTHRO", "AODS", "APE", "APED", "APGR", "APTECH", "ARCH", "ART", "ASL", "ASTRON", "ATHL", "AUTO", "BAD", "BBK", "BEHSC", "BGN", "BIO", "BMG", "BMK", "BOT", "BOTANY", "CEST", "CFS", "CHEM", "CHILD", "CHLD", "CHW", "CI", "CIS", "CLTX", "COMM", "CONS", "COUN", "CS", "CSKL", "CSKLS", "CUL", "DA", "DANCE", "DE", "DET", "DH", "DIET", "DNA", "DRD", "ECON", "EDUC", "ELEC", "EMC", "ENGL", "ENGR", "ENVS", "ENVST", "ENVT", "EQSCI", "ERTHS", "ESL", "FASH", "FDNT", "FIRE", "FLORS", "FREN", "GD", "GEOG", "GEOL", "GERM", "GIS", "GUID", "HIST", "HLC", "HLE", "HORT", "HOSP", "HR", "HUMAN", "IED", "INDE", "INTDIS", "ITAL", "JOUR", "KAQUA", "KCOMB", "KFIT", "KINDV", "KINES", "KTEAM", "LIR", "LPE", "MA", "MACH", "MATH", "MEDIA", "METRO", "MICRO", "MUS", "MUSC", "MUSCP", "NR", "NRA", "NRM", "NRV", "OA", "PE", "PHARM", "PHIL", "PHYED", "PHYS", "PHYSC", "PHYSIO", "PLS", "POLS", "PSYCH", "RADT", "RE", "RELS", "SE", "SOC", "SOCS", "SPAN", "SPCH", "SRT", "SURV", "SUSAG", "THAR", "VE", "VIT", "WELD", "WEOC", "WINE", "WRKEX", "WTR", "WWTR"]

        for department in departments:
            yield scrapy.FormRequest.from_response(
                response,
                formname="Form1",
                method="POST",
                formdata={
                    'txtCourseKey': department
                },
                callback=self.parse_for_courses
            )

    def parse_for_courses(self, response):
        rows = response.css("#tblCourseVersions tr")[1:]
        for row in rows:
            relative_url = row.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            course_number = row.css("a::text").extract_first()
            course_title = row.css("td:nth-child(2) ::text").extract_first()
            anchor = course_number + " " + course_title
            yield scrapy.Request(
                url,
                meta={
                    'depth': 2,
                    'hops_from_seed': 2,
                    'source_url': response.url,
                    'source_anchor': anchor
                },
                callback=self.parse_for_files
            )
