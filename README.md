# lotteries
wx自助抽奖小助手

使用方法:
    运行代码,抓包(Windows下可使用fidder/Mac可使用Charles)获取抽奖助手的授权码填入框内,则可自动提交.(下次可直接输入'qwer1234'使用上次的记录,如出现Unauthorized,则需要再次抓包获取授权码)
    如想生成程序,可按下列代码依次执行:
        source /venu/bin/activate
        python3 setup.py py2app
    生成程序只在Mac实验过,Windows上理论也是可行的.
