from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse  # 可以用来返回json数据
from . import web_salt
from .models import *
import json
from django.contrib.auth.decorators import login_required
import threading
import queue
import django.utils.timezone as tz


# Create your views here.

@login_required
def master_list(request):
    class flush_master(threading.Thread):
        def __init__(self, queue):
            threading.Thread.__init__(self)
            self.q = queue
            self.thread_stop = False

        def run(self):

            while not self.thread_stop:
                try:
                    msg = self.q.get(block=True, timeout=5)

                except queue.Empty:
                    self.thread_stop = True
                    break
                wsa = web_salt.web_salt_api(
                    host=msg.master_host,
                    port=msg.master_port,
                    username=msg.master_user,
                    password=msg.master_pwd
                )
                if wsa.login():
                    msg.master_link_stat = True
                else:
                    msg.master_link_stat = False
                msg.save()
                self.q.task_done()

        def stop(self):
            self.thread_stop = True

    if request.method == "GET":
        if 'delete' in request.GET and 'master_host' in request.GET:
            if request.GET.get('delete') == '1':
                salt_master.objects.filter(master_host=request.GET.get('master_host')).delete()
                return HttpResponseRedirect(request.path + '/master_list')
        if 'flush_master' in request.GET:
            if request.GET.get('flush_master') == '1':
                master_all = salt_master.objects.all()
                q = queue.Queue(5)
                wooker = flush_master(q)
                wooker.start()
                for each in master_all:
                    try:
                        q.put(each, block=True, timeout=10)
                    except Exception as e:
                        continue
                q.join()
            return HttpResponseRedirect(request.path + '/master_list')
    posts = salt_master.objects.all()
    return render(request, 'deploy_more/master_list.html', {'posts': posts})


@login_required
def master_add(request):
    def inner_login(req_list):
        try:
            wsa = web_salt.web_salt_api(
                host=req_list.get('master_address'),
                port=req_list.get('master_port'),
                username=req_list.get('master_user'),
                password=req_list.get('master_pwd')
            )
            return wsa
        except Exception as e:
            return None

    def inner_module(req_list, in_link_stat):
        try:
            obj = salt_master.objects.get(master_host=req_list.get('master_address'))
        except Exception as e:
            obj = None
        if obj:
            obj.master_port = req_list.get('master_port')
            obj.master_user = req_list.get('master_user')
            obj.master_pwd = req_list.get('master_pwd')
            obj.master_link_stat = in_link_stat
            obj.save()
        else:
            salt_master(
                master_host=req_list.get('master_address'),
                master_port=req_list.get('master_port'),
                master_user=req_list.get('master_user'),
                master_pwd=req_list.get('master_pwd'),
                master_link_stat=in_link_stat
            ).save()

    if request.method == 'POST':
        ret_status = {'status': 0, 'data': 0}

        wsa = inner_login(request.POST)

        if request.POST.get('master_test') == 'true':
            if wsa:
                try:
                    wsa.login()
                    response = wsa.test()
                    if len(response) > 0:
                        ret_status['data'] = response
                    ret_status['status'] = 700
                except Exception as e:
                    ret_status['status'] = 701
            else:
                ret_status['status'] = 702
        else:

            try:
                link_stat = False
                if wsa:
                    try:
                        if wsa.login():
                            link_stat = True
                    except Exception as e:
                        pass
                inner_module(request.POST, link_stat)
                ret_status['status'] = 800
            except Exception as e:
                ret_status['status'] = 801
        return HttpResponse(json.dumps(ret_status), content_type="application/json")
    if request.method == 'GET':
        if 'master_host' in request.GET:
            posts = salt_master.objects.get(master_host=request.GET.get('master_host'))
            return render(request, 'deploy_more/master_add.html', {'posts': posts})
        else:
            return render(request, 'deploy_more/master_add.html')


@login_required
def minion_auth(request):
    def inner_login(request_list):
        master_info = salt_master.objects.get(master_host=request_list.get('select_master_host'))
        wsa = web_salt.web_salt_api(
            master_info.master_host,
            master_info.master_port,
            master_info.master_user,
            master_info.master_pwd,
        )
        return wsa

    def inner_json(in_dict):
        content = json.dumps(in_dict, ensure_ascii=False)
        return content

    def inner_model(in_model,master_host,minions,type):

        master_obj=salt_master.objects.get(master_host=master_host)
        del_models_objs = salt_minion_una.objects.filter(minion_una_master=master_host)
        if del_models_objs:
            for i in del_models_objs:
                i.delete()
        del_models_objs = salt_minion_acc.objects.filter(minion_acc_master=master_host)
        if del_models_objs:
            for i in del_models_objs:
                i.delete()

        if type=='acc':
            for each in minions:
                in_model(
                    minion_acc_host=each,
                    minion_acc_master=master_obj,
                ).save()
        if type=='una':

            for each in minions:
                in_model(
                    minion_una_host=each,
                    minion_una_master=master_obj,
                ).save()


    def inner_upstat(wsa, minions):
        test_ping_list = wsa.test()
        for minion in minions:
            if minion.minion_acc_host in test_ping_list[0].keys():
                minion.minion_acc_stat = True
                minion.save()

    ret_posts = {}
    if request.method == 'POST':
        wsa = inner_login(request.POST)
        if 'select_master_host' in request.POST:
            wsa = inner_login(request.POST)
            if not wsa.login():
                return HttpResponse(inner_json({'data': u'主控端登录失败'}), content_type='application/json; charset=utf-8')
            if request.POST.get('type') == 'list_all':
                master_host = request.POST.get('select_master_host')
                minion_acc = wsa.get_minions_acc()

                if minion_acc:
                    inner_model(salt_minion_acc,request.POST.get('select_master_host'),minion_acc,'acc')
                    inner_upstat(wsa, salt_minion_acc.objects.all())

                minion_una = wsa.get_minions_pre()

                if minion_una:
                    inner_model(salt_minion_una, request.POST.get('select_master_host'),minion_una,'una')

                ret_minion_una = salt_minion_una.objects.all()
                ret_minion_acc = salt_minion_acc.objects.all()



                ret_dict={'minion_acc':{'draw':0,'recordsTotal':0,'recordsFiltered':0,'data':[]},'minion_una':{'draw':0,'recordsTotal':0,'recordsFiltered':0,'data':[]}}
                if len(ret_minion_acc)>0:
                    ret_dict['minion_acc']['draw']=1
                    ret_dict['minion_acc']['recordsTotal']=len(ret_minion_acc)
                    ret_dict['minion_acc']['recordsFiltered'] = len(ret_minion_acc)
                    for i in ret_minion_acc:
                        index = 1
                        ret_dict['minion_acc']['data'].append({
                            'id':index,
                            'minion_acc_host':i.minion_acc_host,
                            'minion_acc_master':i.minion_acc_master.master_host,
                            'minion_acc_stat':i.minion_acc_stat,
                            'minion_acc_time':str(i.minion_acc_time)
                        })
                        index = index + 1

                if len(ret_minion_una) > 0:
                    ret_dict['minion_una']['draw'] = 1
                    ret_dict['minion_una']['recordsTotal'] = len(ret_minion_una)
                    ret_dict['minion_una']['recordsFiltered'] = len(ret_minion_una)
                    index=1
                    for i in ret_minion_una:
                        ret_dict['minion_una']['data'].append({
                            'id':index,
                            'minion_una_host':i.minion_una_host,
                            'minion_una_master':i.minion_una_master.master_host,
                            'minion_una_time':str(i.minion_una_time)
                        })


                return HttpResponse(json.dumps(ret_dict), content_type="application/json")

        return HttpResponse(inner_json({'data': u'获取Keys失败'}), content_type='application/json; charset=utf-8')

    if request.method == 'GET':
        ret_posts['masters'] = salt_master.objects.all()
        return render(request, 'deploy_more/minion_auth.html', {'posts': ret_posts})
