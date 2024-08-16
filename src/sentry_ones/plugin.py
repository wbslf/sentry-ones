# coding: utf-8
# -*- coding: utf-8 -*-
import datetime
import json
import urlparse
from sentry.plugins.bases.notify import NotificationPlugin
from sentry.utils.safe import safe_execute
from finger_print import Middleware
from .forms import ONESOptionsForm
import sentry_ones
from sentry.integrations import FeatureDescription, IntegrationFeatures

class OnesPlugin(NotificationPlugin):
  author="mudongshier"
  author_url="https://github.com/wbslf/sentry-ones"
  title = "Ones"
  slug = 'Ones'
  conf_key = slug
  conf_title = title
  version = sentry_ones.VERSION
  description = "Create issues in Ones from Sentry issues"
  project_conf_form = ONESOptionsForm
  feature_descriptions = [
        FeatureDescription(
            """
            Configure rule based outgoing HTTP POST requests from Sentry.
            """,
            IntegrationFeatures.ALERT_RULE,
        )
    ]

  def has_project_conf(self):
        return True

  #校验必填项是否填写完整
  def is_configured(self,project, **kwargs):
    return all((self.get_option(k, project) for k in ("email", "password","assign","project_uuid")))
  
  def notify_users(self, group, event, triggering_rules, fail_silently=False, **kwargs):
        safe_execute(self.create_ones_issue, group, event,  _with_transaction=False)
  
  def get_domain(slef,url):
    parsed_url = urlparse.urlparse(url)
    return parsed_url.netloc

  def get_summary(self,group,event):
      show_log = self.get_option("show_log",group.project)
      title = u'Sentry报警'
      project = event.project.slug
      message = event.title or event.message
      domain_url = event.get_tag('url')
      domain = self.get_domain(domain_url)
      print('entry show_log',show_log)
      if show_log == 'show':
          print('entry show_log=show')
          print(u"title:{title};project:{project};message:{message}".format(
              title=title,project=project,message=message
          ))
      
      return u"{title}-{project}-{message}-{domain}".format(
          title=title,
          project=project,
          message=message,
          domain=domain
      )
  
  
  def get_desc(self,group,event):
      show_log = self.get_option("show_log",group.project)
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
      print('entry show_log',show_log)
      
      tags = event.tags
      browser = event.get_tag('browser')
      release = event.get_tag('release')
      domain_url = event.get_tag('url')
      # 获取当前时间
      now = datetime.datetime.now()

      # 格式化时间为 '年-月-日 时:分:秒'
      formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')

      if show_log == 'show':
          print('entry show_log=show')
          # 打印标签和值
          for tag, value in tags:
            print(u"Tag: {tag}, Value: {value}".format(tag=tag,value=value))
          print(u"url:{url};project:{project};message:{message};stacktrace:{stacktrace};tags={tags}".format(
              url=url,
              project=project,
              message=message,
              stacktrace=stacktrace,
              tags=tags
          ))
      return u"<p>本次报错时间:{formatted_time}</p>\n<p><a href=\"{url}\" target=\"_blank\">查看详情</a></p>\n<p>Sentry链接:{url})</p>\n<p>项目来源：{project}</p>\n<p>event信息:{message}</p>\n<p>报错信息：{stacktrace}</p>\n<p>报错网址：{domain_url}</p>\n<p>浏览器信息：{browser}</p>\n<p>版本信息：{release}</p>\n<p>其他tags:{tags}</p>\n<p>\n<br/><hr/><br/>".format(
          formatted_time=formatted_time,
          url=url,
          project=project,
          message=message,
          stacktrace=stacktrace,
          tags=tags,
          browser=browser,
          release=release,
          domain_url=domain_url,
      )
  

  def create_ones_issue(self, group, event, **kwargs):
     #校验必填项
     if not self.is_configured(group.project):
          return
     if group.is_ignored():
            return
     
     config = {
        "email": self.get_option("email",group.project),
        "password": self.get_option("password",group.project),
        "assign": self.get_option("assign",group.project),
        "project_uuid": self.get_option("project_uuid",group.project),
        "issue_type_uuid": "LpALYBma",
        "summary": self.get_summary(group=group,event=event),
        "desc": self.get_desc(group=group,event=event),
        "show_log": self.get_option("show_log",group.project),
     }

     if self.get_option("issue_type_uuid",group.project):
         config["issue_type_uuid"] = self.get_option("issue_type_uuid",group.project)
      
     middleware = Middleware(config)
     middleware.run()
  
  
     
       
       


  