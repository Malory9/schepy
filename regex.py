# coding: utf-8
"""
词法分析用的正则库

regex表示如下几种: (按顺序递归解析即可满足优先级)
1. 基本 由单个字符组成
2. r|s型, L(r|s) = L(r) | L(r)
3. rs型, L(rs) = L(r)L(s)
4. r*型, L(r*) = L(r)*
5. (r)型, L((r)) = L(r), 只调整优先级
"""

from functools import partial
from operator import and_

from fa import NFA, DFA, NFANode, DFANode


class RegexError(Exception):
    pass


class Regex(object):

    _cache = {}

    def __init__(self):
        pass

    @classmethod
    def is_regex(cls, pattern):
        if pattern in cls._cache:
            return cls._cache[pattern]
        cache = cls._cache
        #print 'is_regex: ', pattern
        if len(pattern) < 1:
            return False
        if cls.is_base(pattern):
            cache[pattern] = True
            return True
        if pattern[0] == '(' and pattern[-1] == ')':
            cache[pattern] = cls.is_regex(pattern[1:-1])
            return cache[pattern]
        if pattern[-1] == '*':
            cache[pattern] = cls.is_regex(pattern[:-1])
            return cache[pattern]
        for i in range(1, len(pattern)):
            # print pattern[:i], pattern[i:]
            tmp = cls.is_regex(pattern[:i])
            if pattern[i] == '|' and tmp and cls.is_regex(pattern[i+1:]):
                cache[pattern] = True
                return True
            if cls.is_regex(pattern[i:]) and tmp:
                cache[pattern] = True
                return True
        cache[pattern] = False
        return False


    @classmethod
    def is_base(cls, pattern):
        if len(pattern) == 1:
            return pattern not in list("()*")
        return pattern in ["\(", "\)", "\*"]


is_regex = Regex.is_regex


def compile_nfa(pattern):
    """
    :param pattern: 正则
    :return: NFA
    """
    print 'compile nfa [%s]' % (pattern, )
    assert isinstance(pattern, str)
    if len(pattern) == 1:
        nfa = NFA()
        enode = NFANode()
        enode.end = True
        nfa.start.next[pattern] = {enode}
        nfa.end.add(enode)
        return nfa
    elif 0 < pattern.find('|') and and_(*map(is_regex, pattern.split('|', 1))):
        print 'r|s型'
        l = pattern.find('|')
        s1, s2 = pattern[:l], pattern[l+1:]
        nfa1, nfa2 = map(compile_nfa, [s1, s2])
        nfa = NFA()
        nfa.start.next["ep"] = set()
        nfa.start.next["ep"].update([nfa1.start, nfa2.start])
        enode = NFANode()
        enode.end = True
        nfa.end.add(enode)
        for node in nfa1.end | nfa2.end:
            if "ep" not in node.next:
                node.next["ep"] = set()
            node.next["ep"].add(enode)
            node.end = False
        nfa1.end, nfa2.end = set(), set()
        return nfa
    else:
        for i in range(1, len(pattern)):
            s1, s2 = pattern[:i], pattern[i:]
            if is_regex(s1) and is_regex(s2):
                print 'rs 连接型'
                nfa1, nfa2 = map(compile_nfa, [s1, s2])
                nfa = NFA()
                snode = nfa.start
                enode = NFANode()
                enode.end = True
                nfa.end = {enode}
                for node in nfa1.end:
                    node.end = False
                    if "ep" not in node.next:
                        node.next["ep"] = set()
                    node.next["ep"].add(nfa2.start)
                for node in nfa2.end:
                    node.end = False
                    if "ep" not in node.next:
                        node.next["ep"] = set()
                    node.next["ep"].add(enode)
                snode.next["ep"] = {nfa1.start}   #虽然我觉得nfa.start = {nfa1.start} 也可以 , 还是按照教材把
                return nfa
        if pattern[-1] == '*' and is_regex(pattern[:-1]):
            print 'r* 型'
            nfa0 = compile_nfa(pattern[:-1])
            nfa = NFA()
            snode = nfa.start
            enode = NFANode()
            enode.end = True
            nfa.end.add(enode)
            snode.next["ep"] = {enode, nfa0.start}
            for node in nfa0.end:
                if "ep" not in node.next:
                    node.next["ep"] = set()
                node.next["ep"].update([nfa0.start, enode])
                node.end = False
            nfa0.end = set()
            return nfa
        elif pattern[-1] == ')' and pattern[0] == '(' and is_regex(pattern):
            print '(r)型'
            return compile_nfa(pattern[1:-1])
        else:
            print 'Excuse me? What the fuck?'
            raise RegexError()


def compile_dfa(pattern):
    return compile_nfa(pattern).convert_dfa()


if __name__ == '__main__':
    #print Regex.is_regex("(")
    #print is_regex("(ab")
    #print Regex.is_regex("(*djwjevsfsfsfswsfafasdasdanr3us)")
    #print Regex._cache
    #print len(Regex._cache)
    nfa = compile_nfa(raw_input())
    nfa.draw()
    dfa = nfa.convert_dfa()
    dfa.draw()
