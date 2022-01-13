from elasticsearch import Elasticsearch
from util.config import config


class ElasticService:
    def __init__(self):
        hosts = config.elastic.hosts
        self.client = Elasticsearch(hosts=hosts)
