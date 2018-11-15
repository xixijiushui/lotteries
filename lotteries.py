#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from tkinter import *
import tkinter as tk

authorization = ''

with open('authorization.txt', 'r') as ra:
    content = ra.readlines()[0]
    authorization = content

# 请求头
headers = {
    'Authorization': authorization,
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34 MicroMessenger/6.7.2 NetType/WIFI Language/zh_CN',
    'Content-Type': 'application/json',
    'version': '0.2.1',
    'Referer': 'https://servicewechat.com/wx01bb1ef166cd3f4e/144/page-frame.html',
    'Accept-Language': 'zh-cn'
}
# 存放获取的数据信息
lotteries = []
# 存放成功参与的信息
info_arr = []


# 获取每日福利
def load_public():
    global lotteries
    content_listbox.grid(row=3, column=0, columnspan=5)
    content_listbox.delete(0, END)
    public_url = 'https://lucky.nocode.com/public_lottery?page=1&size=5'

    res = requests.get(public_url, headers=headers, verify=False)
    if res.status_code == 200:
        # 请求成功,将数据加到组里
        lotteries += res.json().get('data')
        # 加载自助福利
        load_square()
    else:
        s = '每日福利' + str(res.status_code) + res.text
        content_listbox.insert(0, s)


# 获取自助福利
def load_square():
    global lotteries
    square_url = 'https://lucky.nocode.com/square'

    res = requests.get(square_url, headers=headers, verify=False)
    old_url = ''
    if res.status_code == 200:
        # 判断有无更多数据
        url = res.json().get('links').get('next')
        if url != None:
            # 如果存在更多数据,加载更多数据(这边不需要把首页数据加载进来,因为后面请求的更多数据包含这些数据)
            load_more('https://lucky.nocode.com' + url)
        else:
            # 不存在更多,加入组,提交抽奖
            lotteries += res.json().get('data')
            judge_info()
    else:
        s = '自助福利' + str(res.status_code) + res.text
        content_listbox.insert(0, s)

# 加载更多自多福利
def load_more(url):
    global lotteries

    res = requests.get(url, headers=headers, verify=False)
    if res.status_code == 200:
        new_url = res.json().get('links').get('next')
        # 存在更多数据,先将请求到的数据加到组,再去请求更多数据,直到没有更多数据,提交抽奖信息
        lotteries += res.json().get('data')
        if new_url != None:
            load_more('https://lucky.nocode.com' + new_url)
        else:
            judge_info()
    else:
        s = '更多福利' + str(res.status_code) + res.text
        content_listbox.insert(0, s)

import threading
mutex = threading.Lock()
# 开启多线程提交参与信息
def judge_info():
    global lotteries, info_arr

    join_url = 'https://lucky.nocode.com/lottery/{id}/join'

    for lottery in lotteries:
        # 已经抽过,则跳过
        if lottery.get('joined'):
            s = '已经参与过抽奖: <<%s>>' % lottery.get('prizes').get('data')[0].get('name')
            print(s)
            try:
                content_listbox.insert(0, s)
            except:
                pass
            continue

        # 已经结束,跳过
        if lottery.get('draw_type') == 'user' and lottery.get('user_count') >= lottery.get('min_user_count'):
            s = '已经结束: <<%s>>' % lottery.get('prizes').get('data')[0].get('name')
            try:
                content_listbox.insert(0, s)
            except:
                pass
            continue

        t = threading.Thread(target=post_info, args=(lottery, join_url))
        t.start()
        t.join()

    print('*' * 10 + '完成所有请求' + '*' * 10)
    if len(info_arr) > 0:
        for s in info_arr:
            try:
                content_listbox.insert(0, s)
            except:
                print(s)

# 提交请求
def post_info(lottery, join_url):
    global info_arr
    res = requests.post(join_url.format(id=lottery.get('id')), headers=headers, verify=False)
    data = res.json()

    print('-' * 10)
    if res.status_code == 200 and 'errors' not in data:
        s = '成功参与抽奖: <<%s>>' % lottery.get('prizes').get('data')[0].get('name')
        print(s)
        mutexFlag = mutex.acquire(True)
        if mutexFlag:
            info_arr.append(s)
            mutex.release()

# 处理输入的内容
def calculate_data():
    global authorization, headers
    remind_label.grid_forget()
    input_content = input_text.get()
    if input_content == '':
        remind_label.grid(row=2, column=0)
        remind_label['text'] = '请输入内容'
        return
    elif input_content != 'qwer1234':
        authorization = input_content
        with open('authorization.txt', 'w') as wa:
            wa.write(authorization)
    headers['Authorization'] = authorization
    load_public()

root = Tk(className='小助手')

title_label = Label(root, text='自助抽奖小程序')
title_label.grid(row=0, columnspan=5)

input_label = Label(root, text='授权码')
input_label.grid(row=1, column=0)

input_text = Entry(root)
input_text.grid(row=1, column=1, columnspan=4)
input_text.insert(0, '')

remind_label = Label(root)
remind_label.grid(row=2, column=0)
remind_label.grid_forget()

submit_btn = Button(root, text='提交', command=calculate_data)
submit_btn.grid(row=2, column=4, sticky=tk.E)

content_listbox = Listbox(root)

root.mainloop()


