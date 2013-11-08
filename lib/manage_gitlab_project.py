#!/usr/bin/env python
#Created by Sam Gleske
#MIT License
#Created Tue Sep 10 23:01:08 EDT 2013

from sys import argv,exit,stderr
from optparse import OptionParser
import os
import gitlab



try:
  token_secret=os.environ['gitlab_user_token_secret']
  gitlab_url=os.environ['gitlab_url']
  gitlab_namespace=os.environ['gitlab_namespace']
  gitlab_user=os.environ['gitlab_user']
except KeyError:
  print >> stderr, "Environment config missing.  Do not run this script standalone."
  exit(1)
parser = OptionParser()
parser.add_option("--issues",dest="issues",action="store_true",default=False)
parser.add_option("--wall",dest="wall",action="store_true",default=False)
parser.add_option("--merge",dest="merge",action="store_true",default=False)
parser.add_option("--wiki",dest="wiki",action="store_true",default=False)
parser.add_option("--snippets",dest="snippets",action="store_true",default=False)
parser.add_option("--public",dest="public",action="store_true",default=False)
parser.add_option("--create",dest="create",action="store_true",default=False)
parser.add_option("--delete",dest="delete",action="store_true",default=False)
parser.add_option("--desc",dest="desc",metavar="DESC",default=False)
(options,args) = parser.parse_args()
if len(args) == 0:
  print >> stderr, "No project name specified.  Do not run this script standalone."
  exit(1)
elif len(args) > 1:
  print >> stderr, "Too many arguments.  Do not run this script standalone."
  exit(1)

project_name=args[0]

git=gitlab.Gitlab(host=gitlab_url,token=token_secret)

def findgroup(gname):
  #Locate the group
  page=1
  while len(git.getgroups(page=page)) > 0:
    for group in git.getgroups(page=page):
      if group['name'] == gname:
        return group
    page += 1
  else:
    print >> stderr, "Project namespace (user or group) not found or user does not have permission of existing group."
    print >> stderr, "gitlab-mirrors will not automatically create the project namespace."
    exit(1)

def findproject(gname,pname,user=False):
  page=1
  while len(git.getprojects(page=page)) > 0:
    for project in git.getprojects(page=page):
      if not user and project['namespace']['name'] == gname and project['name'] == pname:
        return project
      elif user and project['namespace']['path'] == gname and project['name'] == pname:
        return project
    page += 1
  else:
    return False

def createproject(pname):
  if len(options.desc) == 0:
    if options.public:
      description="Public mirror of %s." % project_name
    else:
      description="Git mirror of %s." % project_name
  else:
    description=options.desc
  new_project=git.createproject(pname,description=description,issues_enabled=int(options.issues),wall_enabled=int(options.wall),merge_requests_enabled=int(options.merge),wiki_enabled=int(options.wiki),snippets_enabled=int(options.snippets),public=int(options.public))
  if gitlab_user != gitlab_namespace:
    new_project=findproject(gitlab_user,pname,user=True)
    new_project=git.moveproject(found_group['id'],new_project['id'])
  if findproject(gitlab_namespace,pname):
    return findproject(gitlab_namespace,pname)
  else:
    return False

if options.create:
  found_group=findgroup(gitlab_namespace)
  found_project=findproject(gitlab_namespace,project_name)

  if not found_project:
    found_project=createproject(project_name)
    if not found_project:
      print >> stderr, "There was a problem creating {group}/{project}.  Did you give {user} user Admin rights in gitlab?".format(group=gitlab_namespace,project=project_name,user=gitlab_user)
      exit(1)

  print found_project['ssh_url_to_repo']
else:
  print >> stderr, "No --create or --delete option added."
  exit(1)
