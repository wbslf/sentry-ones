# coding: utf-8
# -*- coding: utf-8 -*-
from client import OnesClient
import hashlib

class Middleware:
    def __init__(self, config):
        self.client = OnesClient(config['email'], config['password'])
        self.assign = config['assign']
        self.summary = config['summary']
        self.project_uuid = config['project_uuid']
        self.issue_type_uuid = config.get('issue_type_uuid', 'LpALYBma')
        self.desc = config.get('desc', '')
        self.show_log = config['show_log']

    def generate_task_uuid(self, summary):
        # 确保 summary 是一个 Unicode 字符串
        if isinstance(summary, str):
            summary = summary.decode('utf-8')
        # Use SHA-256 hash and take the first 16 characters
        return hashlib.sha256(summary.encode('utf-8')).hexdigest()[:16]
    
    #找到task_info  field_values中的某个值
    def findFieldByFieldUUid(self,field_values,field_uuid):
       cur_value = None
       for field in field_values:
          if field["field_uuid"] == field_uuid:
             cur_value = field['value']
             break
       return cur_value

    def run(self):
        task_uuid = self.generate_task_uuid(self.summary)
        self.client.login()
        if self.show_log == 'show':
            print('show_log:login success')
        # #搜索是否已存在
        task_info = self.client.search_task(task_uuid,self.show_log) 
        # print(task_info)
        if self.show_log == 'show':
            print('show_log: task_info has search')

        if task_info:
           #如果已经存在，检测一下存在的状态
          #  print(task_info,'task_info')
           if self.show_log == 'show':
            print('show_log: task_info is exist')
           task_status = task_info['status_uuid']
           #更新ones单的详情信息
           self.client.update_task_desc(task_info,self.desc,self.show_log)

            #获取当前查询到的迭代
           cur_iteration = self.findFieldByFieldUUid(task_info["field_values"],'field011')
           #查询当前应该放置的迭代
           target_cur_iteration = self.client.select_task_iteration(task_info['project_uuid'],task_info,self.show_log)
           print('旧迭代',cur_iteration,'新迭代',target_cur_iteration)
           if cur_iteration != target_cur_iteration:
            #更新ones单的迭代为最近的迭代
            self.client.update_task_iteration(task_info,self.show_log)
           print('task_status',task_status)
           if task_status != 'F3uKdez3' and task_status != 'TEBrcHXs':
               print('entry update status')
               #更新ones单的状态为待开发
               self.client.update_task_init_status(task_info,self.show_log)
              
        else:
          #如果不存在，则直接新建
          if self.show_log == 'show':
            print('show_log: task_info is not exist')
          self.client.create_task(task_uuid,self.assign, self.summary, self.project_uuid, self.issue_type_uuid, self.desc,self.show_log)
          
        

        
