from sentry.plugins.bases.issue import IssuePlugin
from sentry.utils.safe import safe_execute
import json
import string
import random
from finger_print import Middleware

class  OnesPlugin(IssuePlugin):
  title = "Ones"
  slug = 'Ones'
  conf_key = slug
  conf_title = title
  description = "Create issues in Ones from Sentry issues"

  token = None

  def has_project_conf(self):
        return True

  #校验必填项是否填写完整
  def is_configured(self,project, **kwargs):
    return all((self.get_option(k, project) for k in ("email", "password","assign","project_uuid")))
  
  def notify_users(self, group, event, triggering_rules, fail_silently=False, **kwargs):
        safe_execute(self.create_ones_issue, group, event,  _with_transaction=False)

  def get_summary(self,group,event):
      title = self.get_option('title', group.project)
      project = event.project.slug
      message = event.title or event.message
      return f"{title}-{project}-{message}"
  
  def get_desc(self,group,event):
      url = u"{}events/{}/".format(group.get_absolute_url(), event.event_id)
      project = event.project.slug
      message = event.title or event.message
      stacktrace = ''
      for stack in event.get_raw_data().get('stacktrace', { 'frames': [] }).get('frames', []):
            stacktrace += u"{filename} in {method} at line {lineno}\n".format(
                filename=stack['filename'],
                method=stack['function'],
                lineno=stack['lineno']
            )
      return f"
        <p>[查看详情]({url})</p>\n
        <p>项目来源：{project}</p>\n
        <p>event信息：{message}</p>\n
        <p>报错信息：{stacktrace}</p>\n
        <p>event结构：{event}</p>\n
        <p>group结构：{group}</p>\n
        "
  
  def create_ones_issue(self, group, event, **kwargs):
     #校验必填项
     if not self.is_configured(group.project):
          return
     if group.is_ignored():
            return
     
     config = {
        "email": self.get_options("email",group.project),
        "password": self.get_options("password",group.project),
        "assign": self.get_options("assign",group.project),
        "project_uuid": self.get_options("project_uuid",group.project),
        "issue_type_uuid": "LpALYBma",
        "summary": self.get_summary(group=group,event=event),
        "desc": self.get_desc(group=group,event=event)
     }

     if self.get_options("project_uuid",group.project):
         config["issue_type_uuid"] = self.get_options("project_uuid",group.project)
      
     middleware = Middleware(config)
     middleware.run()
  
  
     
       
       


  