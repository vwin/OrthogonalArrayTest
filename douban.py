from OAT import *
import json
import requests
from functools import partial
from nose.tools import *


class check_response:
    @staticmethod
    def check_result(response, params, expectNum=None):
        # 由于搜索结果存在模糊匹配的情况，这里简单处理只校验第一个返回结果的正确性
        if expectNum is not None:
            # 期望结果数目不为None时，只判断返回结果数目
            eq_(
                expectNum,
                len(response["subjects"]),
                "{0}!={1}".format(expectNum, len(response["subjects"])),
            )
        else:
            if not response["subjects"]:
                # 结果为空，直接返回失败
                assert False
            else:
                # 结果不为空，校验第一个结果
                subject = response["subjects"][0]
                # 先校验搜索条件tag
                if params.get("tag"):
                    for word in params["tag"].split(","):
                        genres = subject["genres"]
                        ok_(word in genres, "Check {0} failed!".format(word))

                # 再校验搜索条件q
                elif params.get("q"):
                    # 依次判断片名，导演或演员中是否含有搜索词，任意一个含有则返回成功
                    for word in params["q"].split(","):
                        title = [subject["title"]]
                        casts = [i["name"] for i in subject["casts"]]
                        directors = [i["name"] for i in subject["directors"]]
                        total = title + casts + directors
                        ok_(
                            any(word.lower() in i.lower() for i in total),
                            "Check {0} failed!".format(word),
                        )


class test_douban:
    """
    豆瓣搜索接口测试demo,文档地址 https://developers.douban.com/wiki/?title=movie_v2#search
    """

    def __init__(self):
        pass

    def search(self, params, expectNum=None):
        url = "https://api.douban.com/v2/movie/search"
        r = requests.get(url, params=params)
        print("Search Params:\n", json.dumps(params, ensure_ascii=False))
        print("Search Response:\n", json.dumps(r.json(), ensure_ascii=False, indent=4))
        code = r.json().get("code", 0)
        if code > 0:
            assert False, "Invoke Error.Code:\t{0}".format(code)
        else:
            # 校验搜索结果是否与搜索词匹配
            check_response.check_result(r.json(), params, expectNum)

    def test_q(self):
        # 校验搜索条件
        qs = [
            u"白夜追凶",
            u"大话西游",
            u"周星驰",
            u"张艺谋",
            u"周星驰,吴孟达",
            u"张艺谋,巩俐",
            u"周星驰,西游",
            u"白夜追凶,潘粤明",
        ]
        tags = [u"科幻", u"喜剧", u"动作", u"犯罪", u"科幻,喜剧", u"动作,犯罪"]
        starts = [0, 10, 20]
        counts = [20, 10, 5]

        # 生成原始测试数据 （有序数组）
        cases = OrderedDict(
            [("q", qs), ("tag", tags), ("start", starts), ("count", counts)]
        )

        # 使用正交表裁剪生成测试集
        cases = OAT().genSets(cases, mode=1, num=0)
        print(json.dumps(cases))
        # 执行测试用例
        for case in cases:
            f = partial(self.search, case)
            f.description = json.dumps(case, ensure_ascii=False)
            yield (f,)
