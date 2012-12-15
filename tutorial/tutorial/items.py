# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class NVForumItem(Item):
    # define the fields for your item here like:
    # name = Field()
    user = Field() #username of poster
    board = Field() #which forum
    board_num = Field()
    topic = Field() #what was the topic
    topic_num = Field()
    timestamp = Field() # time and date of post
    op = Field() #was this the original poster?
    
