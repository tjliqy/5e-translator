from abc import ABCMeta, abstractmethod
from config import LINE_TAGS
from enum import Enum, auto

class NodeType(Enum):
    CONTENT = auto(0)
    LINE = auto(1)
    BR = auto()
    TABLE = auto()
    TITLE_SECONDARY = auto()
    TITLE_PRIMARY = auto()

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class NodeChecker():
    # @abstractmethod
    # def isPrimaryTitle(self, node):
    #     pass
    # @abstractmethod
    # def isSecondaryTitle(self, node):
    #     pass
    def rate(self, node) -> (int):
        rate = 100
        conditions = [
            node.name == 'h1', # <h1>title</h1>
            node.name == 'h2', # <h2>title</h2>
            node.name == 'h3', # <h3>title</h3>
            node.name == 'font' and node.get('color') == "#800000", #<font color="#800000">title</font>
            node.name == 'p' and len(list(node.children)) == 1 and list(node.children)[0].name == 'strong' # <p><strong>title</strong></p>
        ]
        for condition in conditions:
            if condition:
                return rate
            rate -= 1
        if self.isLine(node):
            return NodeType.LINE.value
        return NodeType.CONTENT.value
    def isTable(self,node):
        return node.name == 'table'
    def isLine(self, node):
        return node.name in LINE_TAGS
    def isBR(self, node):
        return node.name == 'br'


# BASIC_NODE_CHECKERS = [BasicNodeChecker1(), BasicNodeChecker2()]
