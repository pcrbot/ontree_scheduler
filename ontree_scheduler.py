import os
import sqlite3
from datetime import datetime,timedelta

from nonebot import get_bot 

import hoshino
from hoshino import Service
from hoshino.typing import CQEvent

sv = Service('挂树提醒', enable_on_default=True, help_='挂树提醒')

@sv.on_command('挂树')
async def climb_tree(session):
    #获取上树成员以及其所在群信息
    ctx = session.ctx
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    #连接挂树记录数据库
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    #查询当前状态是否已经上树，如果在挂树则提示，未挂树则上树
    query = cur.execute(f"SELECT COUNT(*) FROM tree WHERE qqid={user_id} AND gid={group_id}")
    for row in query:
        is_ontree = row[0]
    if(is_ontree==1):
        msg = f'>>>挂树计时提醒[!]\n[CQ:at,qq={user_id}]已经挂树\n请勿重复上树'
    else:
        climb_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        climb_stime = datetime.now().strftime("%H:%M:%S")
        loss_time = (datetime.now()+timedelta(minutes=55)).strftime("%Y-%m-%d %H:%M:%S")
        loss_stime = (datetime.now()+timedelta(minutes=55)).strftime("%H:%M:%S")
        cur.execute(f"INSERT INTO tree VALUES(NULL,{user_id},{group_id},\"{loss_time}\")")
        con.commit()
        con.close()
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={user_id}]开始挂树\n因上报时间与游戏时间存在误差\n挂树时长按照55分钟计算\n开始时间:{climb_stime}\n下树期限:{loss_stime}'
    await session.send(msg)

@sv.on_command('取消挂树')
async def down_tree(session):
    #获取下树成员以及其所在群信息
    ctx = session.ctx
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    #连接挂树记录数据库
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    #查询当前状态是否已经下树，如果在挂树则删除记录，未挂树则提示错误
    query = cur.execute(f"SELECT COUNT(*) FROM tree WHERE qqid={user_id} AND gid={group_id}")
    for row in query:
        is_ontree = row[0]
    if(is_ontree==0):
        msg = f'>>>挂树计时提醒[!]\n[CQ:at,qq={user_id}]尚未挂树\n请勿申请下树'
    else:
        cur.execute(f"DELETE FROM tree WHERE qqid={user_id} AND gid={group_id}")
        con.commit()
        con.close()
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={user_id}]已经下树'
    await session.send(msg)

@sv.on_command('sl')
async def sl_down_tree(session):
    #获取下树成员以及其所在群信息
    ctx = session.ctx
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    #连接挂树记录数据库
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    #查询当前状态是否已经下树，如果在挂树则删除记录，未挂树则提示错误
    query = cur.execute(f"SELECT COUNT(*) FROM tree WHERE qqid={user_id} AND gid={group_id}")
    for row in query:
        is_ontree = row[0]
    if(is_ontree!=0):
        cur.execute(f"DELETE FROM tree WHERE qqid={user_id} AND gid={group_id}")
        con.commit()
        con.close()
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={user_id}]已经下树'
        await session.send(msg)


@sv.on_prefix('报刀')
async def baodao_down_tree(bot, ev: CQEvent):
    cmd = ev.raw_message
    content=cmd.split()
    if(len(content)!=2):
        return

    #获取下树成员以及其所在群信息
    user_id = ev['user_id']
    group_id = ev['group_id']
    #连接挂树记录数据库
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    #查询当前状态是否已经下树，如果在挂树则删除记录，未挂树则提示错误
    query = cur.execute(f"SELECT COUNT(*) FROM tree WHERE qqid={user_id} AND gid={group_id}")
    for row in query:
        is_ontree = row[0]
    if(is_ontree!=0):
        cur.execute(f"DELETE FROM tree WHERE qqid={user_id} AND gid={group_id}")
        con.commit()
        con.close()
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={user_id}]已经下树'
        await bot.send(ev,msg)

@sv.on_command('查树')
async def check_tree(session):
    ctx = session.ctx
    group_id = ctx['group_id']
    bot = get_bot()
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    # cur.execute("SELECT qqid,gid,loss_time FROM tree WHERE (strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime'))) BETWEEN 0 AND 6000")
    cur.execute(f"SELECT qqid,(strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime'))) AS rest_time FROM tree WHERE gid={group_id} ORDER BY loss_time ASC")
    query = cur.fetchall()
    msg = ''
    count = 0
    for row in query:
        count += 1
        qq_id = row[0]
        rest_time = row[1]
        # if(".000" in loss_time):
        #     loss_time = loss_time[:-4]
        msg = msg +  f'[CQ:at,qq={qq_id}]预计还剩{rest_time//60}分钟\n'
    if count > 0:
        await bot.send_group_msg(group_id=group_id, message=msg)
    con.commit()
    con.close()
    return
    
@sv.on_command('尾刀')
async def weidao(session):
    ctx = session.ctx
    group_id = ctx['group_id']
    bot = get_bot()
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    # cur.execute("SELECT qqid,gid,loss_time FROM tree WHERE (strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime'))) BETWEEN 0 AND 6000")
    cur.execute(f"SELECT qqid FROM tree WHERE gid={group_id}")
    query = cur.fetchall()
    msg = ''
    count = 0
    for row in query:
        count += 1
        qq_id = row[0]
        msg = msg +  f'[CQ:at,qq={qq_id}]已下树\n'
        cur.execute(f"DELETE FROM tree WHERE qqid={qq_id} AND gid={group_id}")
    if count > 0:
        await bot.send_group_msg(group_id=group_id, message=msg)
    con.commit()
    con.close()
    return
@sv.scheduled_job('interval', minutes=10)
async def ontree_scheduler():
    bot = get_bot()
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    # cur.execute("SELECT qqid,gid,loss_time FROM tree WHERE (strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime'))) BETWEEN 0 AND 6000")
    # cur.execute("SELECT qqid,gid,loss_time FROM tree ORDER BY loss_time ASC")
    cur.execute(f"SELECT qqid,gid,MIN((strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime')))) AS rest_time,COUNT(*) as ontree_count FROM tree GROUP BY gid")
    query = cur.fetchall()
    for row in query:
        qq_id = row[0]
        group_id = row[1]
        rest_time = row[2]
        ontree_count = row[3]
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={qq_id}]最早挂树，预计还剩{rest_time//60}分钟，在树{ontree_count}人'
        await bot.send_group_msg(group_id=group_id, message=msg)
    # for row in query:
    #     qq_id = row[0]
    #     group_id = row[1]
    #     loss_time = row[2][11:]
    #     if(".000" in loss_time):
    #         loss_time = loss_time[:-4]
    #     msg = f'>>>挂树计时提醒，目前最早挂树者：\n[CQ:at,qq={qq_id}]\n预计下树极限时间: {loss_time}，在树{}人'
    #     await bot.send_group_msg(group_id=group_id, message=msg)
    cur.execute("DELETE FROM tree WHERE (strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime')))<0")
    con.commit()
    con.close()
    return