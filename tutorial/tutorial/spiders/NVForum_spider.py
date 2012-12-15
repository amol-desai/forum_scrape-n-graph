from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from tutorial.items import NVForumItem
import re
from scrapy import log
from scrapy.http import Request

class NVForumSpider(CrawlSpider):
    name = "NVForum"
    allowed_domains = ["forums.geforce.com"]
    start_urls = [
        "https://forums.geforce.com/"
    ]
    rules = (
        Rule(SgmlLinkExtractor(allow=("/default/board/.*"),restrict_xpaths=("//h3[@class='board-title']"),unique=True),follow=True,callback="parse_forum"),
        Rule(SgmlLinkExtractor(allow=("/default/topic/.*",),restrict_xpaths=("//div[@class='topic-title']/table/tr/td"),unique=True),follow=True,callback="parse_item")
    )
           
    def parse_forum(self,response):
        hxs = HtmlXPathSelector(response)
        if not hxs.select("//div[@class='topic-title']"):
            self.log("Page of Forums: "+response.url,level=log.DEBUG)
            self.log("parse called by follow = True should take us to the next level")
            yield Request(url=response.url,callback=self.parse_forum)
        else:
            self.log("Page of Topics: "+response.url,level=log.DEBUG)
            if hxs.select("//span[@class='page-num']/text()"):
                self.log("Passing to parse to take care of extracting topics and passing on to parse_item.",level=log.DEBUG)
                #This only happens if this is a request created by parse_forum. If not, it is already taken care of by parse.
                if int(re.match('.*/(\d*)/',response.url).group(1)) > 1:
                    yield Request(url=response.url,callback=self.parse,dont_filter=True)
                curr_page = re.search('(\d*) /.*',(hxs.select("//span[@class='page-num']/text()").extract()[0])).group(1)
                total_pages = re.search('.*/ (\d*)',(hxs.select("//span[@class='page-num']/text()").extract()[0])).group(1)
                self.log(curr_page+" of "+total_pages,log.DEBUG)
                if int(curr_page) == 1:
                    self.log("Requesting URL: "+response.url+str(2)+"/"+" and passing it to parse_forum")
                    yield Request(url=response.url+str(2)+"/",callback=self.parse_forum)
                elif int(curr_page) < int(total_pages):
                    next_page = int(curr_page)+1
                    self.log("Requesting URL: "+(re.match('(.*/)\d*/',response.url).group(1))+str(next_page)+"/"+" and passing it to parse_forum")
                    yield Request(url=(re.match('(.*/)\d*/',response.url).group(1))+str(next_page)+"/",callback=self.parse_forum)
                    self.log((re.match('(.*/)\d*/',response.url).group(1))+str(next_page)+"/",level=log.DEBUG)
        
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        users = hxs.select("//div[@class='profileName']/a/text()").extract()
        board = hxs.select("//span[@class='crumb']/a/text()").extract()
        board_num = hxs.select("//span[@class='crumb']/a/@href").extract()
        topic = hxs.select("//div[@class='topic-title-wrapper']/span/text()").extract()
        timestamps = hxs.select("//div[@class='forumInfo']/text()").extract()
        if hxs.select("//span[@class='page-num']/text()"):
                self.log("This is not the only page",level=log.DEBUG)
                curr_page = re.search('(\d*) /.*',(hxs.select("//span[@class='page-num']/text()").extract()[0])).group(1)
                total_pages = re.search('.*/ (\d*)',(hxs.select("//span[@class='page-num']/text()").extract()[0])).group(1)
                self.log(curr_page+" of "+total_pages,level=log.DEBUG)
                if int(curr_page) == 1:
                    self.log("Requesting URL: "+response.url+str(2)+"/"+" and passing it to parse_item",level=log.DEBUG)
                    yield Request(url=response.url+str(2)+"/",callback=self.parse_item)
                elif int(curr_page) < int(total_pages):
                    next_page = int(curr_page)+1
                    self.log("Requesting URL: "+(re.match('(.*/)\d*/',response.url).group(1))+str(next_page)+"/"+" and passing it to parse_item",level=log.DEBUG)
                    yield Request(url=(re.match('(.*/)\d*/',response.url).group(1))+str(next_page)+"/",callback=self.parse_item)
        else:
            self.log("This is the only page",level=log.DEBUG)
            curr_page = 1
        for i,user in enumerate(users):
            item = NVForumItem()
            item['user'] = user
            item['board'] = board[len(board)-1]
            item['board_num'] = re.match('.*/board/(\d*).*',board_num[len(board_num)-1]).group(1)
            item['topic']=topic[0]
            item['topic_num'] = re.match('.*/topic/(\d*)/.*',response.url).group(1)
            item['timestamp'] = ((re.search('Posted (.*)',timestamps[i]).group(1)).replace(u'\xa0',''))
            if (int(curr_page)==1) and (i==0):
                item['op']=True
            else:
                item['op']=False
            yield item
        return
