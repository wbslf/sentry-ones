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

    def generate_task_uuid(self, summary):
        # Use SHA-256 hash and take the first 16 characters
        return hashlib.sha256(summary.encode('utf-8')).hexdigest()[:16]

    def run(self):
        task_uuid = self.generate_task_uuid(self.summary)
        self.client.login()
        #搜索是否已存在
        task_info = self.client.search_task(task_uuid) 
        # print(task_info)
         
        if task_info:
           #如果已经存在，检测一下存在的状态
          #  print(task_info,'task_info')
           task_status = task_info['status_uuid']
           if task_status != 'F3uKdez3':
               #更新ones单的状态为待开发
               self.client.update_task_init_status(task_info)
               #更新ones单的迭代为最近的迭代
               self.client.update_task_iteration(task_info)
        else:
          #如果不存在，则直接新建
            create_response = self.client.create_task(task_uuid,self.assign, self.summary, self.project_uuid, self.issue_type_uuid, self.desc)
            print("Create Task Response:", create_response)
        

        
