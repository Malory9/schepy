# coding: utf-8

from Queue import Queue

from util import unions
# import crash_on_ipy

# crash_on_ipy.init()


class BaseNode(object):
    """
    FA节点
    self.next {alpha: list(NFANode)} "ep"表示空弧转换
    self.meta {info: val}   例如该节点代表终结符时为哪种token(id, comment, num)
    self.end  是否终结符
    """
    def __init__(self, next_type, **kwargs):
        #self.next = defaultdict(next_type)
        self.next = dict()
        self.meta = dict(kwargs)
        self.end = False

    def __getattr__(self, item):
        if item in self.meta:
            return self.meta[item]
        print 'meta has not this key: ', item
        raise AttributeError


class NFANode(BaseNode):
    """
    NFA节点
    self.next {alpha: list(NFANode)} "ep"表示空弧转换
    self.meta {info: val}   例如该节点代表终结符时为哪种token(id, comment, num)
    self.end  是否终结符
    """
    def __init__(self, **kwargs):
        super(NFANode, self).__init__(next_type=set, **kwargs)

    @property
    def nexts(self):
        return unions([self.next[key] for key in self.next.keys()])


class DFANode(BaseNode):

    def __init__(self, **kwargs):
        super(DFANode, self).__init__(next_type=DFANode, **kwargs)

    @property
    def nexts(self):
        """
        返回可以转移到的下一阶段所有节点组成的list
        """
        return [self.next[key] for key in self.next.keys()]


class FA(object):
    """
    start 起始状态
    alpha 字母表
    end 终结状态
    转换函数在node中体现
    """
    def __init__(self, node_type, alpha=None):
        self.start = node_type()
        self.alpha = alpha or []
        self.end = set()


# @profile
def closure(nodes):
    if not isinstance(nodes, set):
        return closure({nodes})
    que = Queue()
    for node in nodes:
        que.put(node)
    res = set(nodes)
    while not que.empty():
        t = que.get()
        for x in t.next.get("ep", set()):
            if x not in res:
                res.add(x)
                que.put(x)
    return res


def move(t_nodes, a):
    """
    :param t_nodes: T
    :param a: a
    :return: move(T, a)
    """
    return unions([node.next.get(a, set()) for node in t_nodes])


class NFA(FA):

    def __init__(self):
        super(NFA, self).__init__(node_type=NFANode)

    def convert_dfa(self, copy_meta=None):
        """
        :return: 与本nfa等价的dfa
        """
        if copy_meta is None:
            copy_meta = []
        nfa, dfa = self, DFA()
        vis = dict()
        cur_set = closure(nfa.start)
        dfa.start = DFANode(nfa_set=cur_set)
        vis[frozenset(cur_set)] = dfa.start
        que = Queue()
        que.put(cur_set)
        while not que.empty():
            tmp = que.get()
            dfa_node = vis[frozenset(tmp)]
            next_set = unions([set(node.next.keys()) for node in tmp]).difference({"ep"})
            for a in next_set:
                u = closure(move(tmp, a))
                if frozenset(u) not in vis:
                    que.put(u)
                    dfa_node.next[a] = DFANode(nfa_set=u)
                    next_node = dfa_node.next[a]
                    intersection = nfa.end & u
                    if intersection:
                        for key in copy_meta:
                            next_node.meta.setdefault(key, [])
                            next_node.meta[key].extend([node.meta.get(key) for node in intersection])
                        next_node.end = True
                        dfa.end.add(next_node)
                    vis[frozenset(u)] = dfa_node.next[a]
                else:
                    dfa_node.next[a] = vis[frozenset(u)]
        return dfa

    @classmethod
    def combine(cls, *args):
        res = NFA()
        res.start.next["ep"] = set()
        res.end = set()
        for nfa in args:
            res.start.next["ep"].add(nfa.start)
            res.end.update(nfa.end)
        return res

    def draw(self, filename="nfa", show_meta=False):
        """
        :param filename:
        :param show_meta:
        :return: draw a dot file which can be shown by graphviz
        """
        que = Queue()
        que.put(self.start)
        vis = dict()
        cnt = 0
        while not que.empty():
            tmp = que.get()
            if tmp in vis:
                continue
            vis[tmp] = 1
            tmp.meta["id"] = cnt
            cnt += 1
            for x in tmp.nexts:
                que.put(x)
        que = Queue()
        que.put(self.start)
        vis = dict()
        with open(filename+'.dot', 'wt') as f:
            f.write('digraph regex_dfa{\nrankdir=LR;\n')
            while not que.empty():
                tmp = que.get()
                if tmp in vis:
                    continue
                vis[tmp] = 1
                if tmp.end:
                    if show_meta:
                        f.write('\t %d [label="%d %s", shape=doublecircle]\n' % (tmp.id, tmp.id, repr(tmp.meta)))
                    else:
                        f.write('\t %d [label="%d", shape=doublecircle]\n' % (tmp.id, tmp.id))
                else:
                    f.write('\t%d [label=%d]\n' % (tmp.id, tmp.id))
                for key in tmp.next.keys():
                    nexts = tmp.next[key]
                    for u in nexts:
                        f.write('\t%d-> %d [label="%s"]\n' % (tmp.id, u.id, key))
                        que.put(u)
            f.write('}\n')


class DFA(FA):

    def __init__(self):
        super(DFA, self).__init__(node_type=DFANode)

    def generate_id(self):
        que = Queue()
        que.put(self.start)
        cnt = 0
        vis = dict()
        while not que.empty():
            tmp = que.get()
            if tmp in vis:
                continue
            vis[tmp] = 1
            tmp.meta["id"] = cnt
            cnt += 1
            for x in tmp.nexts:
                que.put(x)
