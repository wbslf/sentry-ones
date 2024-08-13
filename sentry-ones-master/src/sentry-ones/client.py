import requests
import uuid
import random
import string
from datetime import datetime

class OnesClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.user_uuid = None
        self.token = None
        self.team_uuid = None
    #登录
    def login(self):
        url = "https://sz.ones.cn/project/api/project/auth/login"
        payload = {
            'email': self.email,
            'password': self.password
        }
        response = requests.post(url, json=payload)
        data = response.json()
        # print("Response data:", data)  # 打印响应数据以便调试

        if response.status_code == 200:
           try:
                self.user_uuid = data['user']['uuid']
                self.token = data['user']['token']
                if 'teams' in data:
                    teams = data['teams']
                    # print("Teams data:", teams)
                    if len(teams) > 0:
                        self.team_uuid = teams[0]['uuid']
                        # print("Team UUID:", self.team_uuid)
                    else:
                        raise KeyError("No teams available in the response")
                else:
                    raise KeyError("Key 'teams' not found in the response")
                print(f"Login successful: user_uuid={self.user_uuid}, team_uuid={self.team_uuid}")
           except KeyError as e:
                raise Exception(f"KeyError: {e} not found in the response")
        else:
            raise Exception(f"Login failed: {data}")

    def generate_key(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    #生成创建ones单的数据
    def get_task_payload(self,task_uuid, assign, summary, project_uuid,cur_iteration, issue_type_uuid='LpALYBma', desc='',status = 'TEBrcHXs'):
        payload = {
            'tasks': [
                {
                    'uuid': task_uuid,   #uuid
                    'owner': self.user_uuid,  # 创建人id
                    'assign': assign,  #负责人id
                    'summary': summary, # 标题
                    'project_uuid': project_uuid,  # 项目uuid  所属项目
                    'parent_uuid': '',
                    'watchers': [self.user_uuid, assign],  #观察者id
                    'issue_type_uuid': issue_type_uuid,  #工作项id类型
                    'desc': desc,  #描述
                    'field_values':[
                        {
                        "field_uuid": "field001",  # 标题
                        "type": 2,
                        "value": summary  
                      },
                       {
                        "field_uuid": "field016",  # 单子描述
                        "type": 20,
                        "value": desc  
                      },
                       {
                        "field_uuid": "field004",  # 负责人
                        "type": 8,
                        "value": self.user_uuid  
                      },
                      {
                        "field_uuid": "field005",  # 状态 默认待开发
                        "type": 12,
                        "value": status
                      },
                      {
                        "field_uuid": "field011",  # 所属迭代
                        "type": 7,
                        "value": cur_iteration  
                      },
                       {
                        "field_uuid": "field012",  # 优先级  默认普通5hWwRTc4
                        "type": 1,
                        "value": "5hWwRTc4"   
                      },
                      {
                        "field_uuid": "field029",  #所属产品
                        "type": 44,
                        "value": [
                            "8QCeEWLZ4PAuCpJo",  #默认ERP5.0基础版
                        ]
                      },
                      {
                        "field_uuid": "Wr1TXpRr",  # 验收人  默认负责人  自定义字段
                        "type": 8,
                        "value": self.user_uuid    
                      },
                       {
                        "field_uuid": "34BcpiNu",  # 优化缺陷类型  默认负责人  alert--异常报错
                        "type": 1,
                        "value": 'M2uBThRJ'   
                      },
                    ]
                }
            ]
        }
        return payload

    #创建ones单
    def create_task(self,task_uuid, assign, summary, project_uuid, issue_type_uuid='LpALYBma', desc=''):
        url = f"https://sz.ones.cn/project/api/project/team/{self.team_uuid}/tasks/add3"
        #创建的taskuuid
        # default_task_uuid = self.user_uuid + self.generate_key()   

        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }

        cur_iteration = self.select_task_iteration(project_uuid,None)

        payload = self.get_task_payload(task_uuid,assign, summary, project_uuid,cur_iteration,issue_type_uuid,desc)

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            if 'bad_tasks' in response_data and len(response_data['bad_tasks']) > 0:
                raise Exception(f"Failed to create task: {response_data['bad_tasks']}")
            if 'tasks' in response_data and len(response_data['tasks']) > 0:
                print("Tasks created successfully:", response_data['tasks'])
                return response_data['tasks']
            else:
                raise Exception("No tasks created, but response was successful.")
        else:
            raise Exception(f"Create issue failed with status code {response.status_code}: {response.text}")
        
    #更新任务的状态，将其更新为待开发
    def update_task_init_status(self,task_info):
        
        url = f"https://sz.ones.cn/project/api/project/team/{self.team_uuid}/task/{task_info["uuid"]}/new_transit"  #状态更新url
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }

        payload = {
            "transition_uuid": "F3uKdez3" 
        }
        try:
          print('updateing')
          print(url,payload)
          response = requests.post(url, json=payload, headers=headers)
          response_data = response.json()
          if response.status_code == 200:
              print(response_data)
              return response_data
          else:
              raise KeyError("update task fail")
        except KeyError as e:
                raise Exception(f"update fail:{response_data}")
        
    #找出最接近的迭代日期
    def find_closest_date(self,data, current_time):
      # 解析每个name并转换为datetime对象
      dates = []
      for item in data:
          try:
              date = datetime.strptime(item['name'], '%Y-%m-%d')
              dates.append({'uuid': item['uuid'], 'name': item['name'], 'date': date})
          except ValueError:
              # 如果解析失败，跳过这个条目
              continue

      # 确保当前时间的日期部分也被考虑
      current_date_only = current_time.date()

      # 过滤出大于等于当前时间的日期
      future_dates = [item for item in dates if item['date'].date() >= current_date_only]

      # 如果有未来的日期或当天的日期，选取最近的一个
      if future_dates:
          closest_date = min(future_dates, key=lambda x: x['date'])
          # 检查是否有与当前时间重合的日期
          if closest_date['date'].date() == current_date_only:
              return {'uuid': closest_date['uuid'], 'name': closest_date['name']}
      else:
          # 如果没有未来日期，选取最近的过去日期
          past_dates = [item for item in dates if item['date'].date() < current_date_only]
          if past_dates:
              closest_date = max(past_dates, key=lambda x: x['date'])
          else:
              # 如果没有任何日期数据，返回None或适当的默认值
              return None

      return {'uuid': closest_date['uuid'], 'name': closest_date['name']}
    
    #选中最接近的迭代uuid
    def select_task_iteration(self,project_uuid,task_info):
        cur_project_uuid = project_uuid
        if task_info:
          cur_project_uuid = task_info['project_uuid']
          dict_result = next((item for item in task_info["field_values"] if item['field_uuid'] == 'field011'),None)
          select_value = dict_result['value']  #当前的迭代
        url = f"https://sz.ones.cn/project/api/project/team/{self.team_uuid}/items/graphql?t=sprint_all_or_project"
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        payload ={
            "query":  "{\n  buckets(groupBy: $groupBy, orderBy: $bucketOrderBy, pagination: {limit: 100, after: \"\", preciseCount: true}) {\n    sprints(orderBy: $orderBy, filterGroup: $filterGroup, limit: 1000) {\n      uuid\n      name\n      project {\n        uuid\n        name\n        isPin\n        namePinyin\n        isCurrentProject(projectUUID: $projectUUID)\n        sprintComponent {\n          uuid\n        }\n      }\n      statusCategory\n    }\n    key\n    pageInfo {\n      count\n      preciseCount\n      totalCount\n      startPos\n      startCursor\n      endPos\n      endCursor\n      hasNextPage\n      unstable\n    }\n  }\n}\n",
            "variables": {
                "filterGroup":[
                    {
                      "project": {
                        "uuid_in": [
                          cur_project_uuid
                        ]
                      },
                      "statusCategory_in": [
                        "in_progress",
                        "to_do"
                      ],
                      "canChangeSprint_equal": 'true',
                    }
                ],
                "groupBy": {
                    "sprints": {}
                },
                "orderBy": {
                    "createTime": 'DESC',
                    "statusCategory": "ASC",
                    "project": {
                      "isCurrentProject": "DESC",
                      "isArchive": "ASC",
                      "isPin": "DESC",
                      "createTime": "DESC"
                    }
                },
                "project_uuid": cur_project_uuid
            }
        }
        try:
          response = requests.post(url, json=payload, headers=headers)
          response_data = response.json()
          if response.status_code == 200:
              iteration_list = response_data['data']['buckets'][0]['sprints']
              # 获取当前时间
              now = datetime.now()
              # print('iteration_list',iteration_list)
              find_data = self.find_closest_date(iteration_list,now)
              return find_data['uuid']
          else:
              print("search iteration list fail")
              return select_value
        except KeyError as e:
                print(f"search iteration list fail:{response_data}")
                return select_value
       
        
    #更新迭代日期
    def update_task_iteration(self,task_info):
         url = f"https://sz.ones.cn/project/api/project/team/{self.team_uuid}/tasks/update3"  #基础更新url
         headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
        
         use_iteration = self.select_task_iteration(None,task_info)

         payload = {
             "tasks": [
                 {
                     "uuid": task_info["uuid"],
                     "field_values": [
                        {
                          "field_uuid": "field011",
                          "type": 7,
                          "value": use_iteration
                        }
                      ]
                 }
             ]
            
         }
         try:
          print('updateing')
          # print(url,payload)
          response = requests.post(url, json=payload, headers=headers)
          response_data = response.json()
          if response.status_code == 200:
              print(response_data)
              return response_data
          else:
              raise KeyError("update task iteration fail")
         except KeyError as e:
                raise Exception(f"update task iteration fail :{response_data}")

    #根据task_uuid,获取信息
    def search_task(self,task_uuid):
        url = f"https://sz.ones.cn/project/api/project/team/{self.team_uuid}/task/{task_uuid}/info"

        headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }

        payload = {
          
        }
        try:
          response = requests.get(url, json=payload, headers=headers)
          response_data = response.json()
          if response.status_code == 200:
              # print(response_data)
              return response_data
          else:
              print("search task fail")
        except KeyError as e:
                print(f"search fail:{response_data}")
        return None

        
        
