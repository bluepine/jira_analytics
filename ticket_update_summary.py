#python 2.x
from jira import JIRA
import dateutil.parser
import os
from datetime import datetime, timedelta

# complete set: set([u'Defect Category', u'labels', u'Epic Link', u'assignee', u'Version', u'Attachment', u'Parent', u'Workflow', u'Story Points', u'Component', u'priority', u'Link', u'Key', u'Epic Child', u'status', u'Rank (Legacy)', u'Fix Version', u'description', u'reporter', u'Flagged', u'Comment', u'summary', u'project', u'RemoteIssueLink', u'Epic Name', u'issuetype', u'Sprint', u'resolution', u'Business Unit'])

HISTORY_ITEM_FIELDS = set(['assignee', 'Attachment', 'Story Points', 'status', 'Comment', 'summary', 'resolution'])

def to_str(obj):
    if None == obj:
        return 'None'
    else:
        if isinstance(obj, basestring):
            return obj.strip()
        else:
            return str(obj).strip()

def last_relevant_update_date(issue):
    changelog = issue.changelog
    last_date = None
    for history in changelog.histories:
        for item in history.items:
            if item.field in HISTORY_ITEM_FIELDS:
                d = dateutil.parser.parse(history.created.strip())
                if not last_date or d > last_date:
                    last_date = d
    if last_date:
        return last_date.replace(tzinfo=None)
    else:
        return None

def print_issue_summary(issue, cutoff_date=None):
        ret = ''
        changelog = issue.changelog
        header_printed = False
        attachment_dict = {}
        for history in changelog.histories:
            for item in history.items:
                if cutoff_date:
                    d = dateutil.parser.parse(history.created.strip()).replace(tzinfo=None)
                    if d < cutoff_date:
                        continue
                if item.field in HISTORY_ITEM_FIELDS:
                    if not header_printed:
                        ret += u"{0}: {1} -> {2} {{".format(issue.key, issue.fields.summary, issue.fields.assignee).encode('ascii', 'ignore') + '\n'
                        if None != issue.fields.attachment:
                            for a in issue.fields.attachment:
                                attachment_dict[to_str(a.filename)] = a.content
                        header_printed = True
                    # print item.field, history.created, item.fromString, item.toString
                    if item.field == 'Attachment' and to_str(item.toString) in attachment_dict.keys():
                        ret += u"    {0} updated {1} from {2} to {3}".format(item.field, to_str(history.created), item.fromString, attachment_dict[to_str(item.toString)]).encode('ascii', 'ignore') + '\n'
                    else:
                        ret += u"    {0} updated {1} from {2} to {3}".format(item.field, to_str(history.created), item.fromString, item.toString).encode('ascii', 'ignore') + '\n'
        if header_printed:
            ret += '}\n'
        return ret

def query(q):
    LARGE_NUMBER = 100000
    options = {
        'server': 'http://tickets.turner.com'}
    days_range = 70
    date_days_range_start = datetime.now() - timedelta(days=days_range)
    #make sure your machine's local time zone matches that of jira server!
    #jira = JIRA(options, basic_auth=(os.environ['JIRA_USERNAME'], os.environ['JIRA_PASSWORD']))
    jira = JIRA(options)
    #update your query here using jql: https://confluence.atlassian.com/jiracore/blog/2015/07/search-jira-like-a-boss-with-jql
    #project = TITAN AND resolution = Unresolved and (assignee=c-expansion-tvu or assignee=c-nbapossible-kday or assignee=swei) ORDER BY priority DESC, updated DESC
    issues = jira.search_issues(q, maxResults=LARGE_NUMBER, fields='updated,assignee,summary,attachments', expand='changelog')
    zipped = zip(issues, [last_relevant_update_date(issue) for issue in issues])
    zipped = filter(lambda x: x[1] and x[1] > date_days_range_start, zipped)
    zipped = sorted(zipped, key = lambda x: x[1], reverse=True)
    ret = u"{0} issues were updated in the last {1} days for {2}".format(str(len(zipped)), str(days_range), u", ".join(list(HISTORY_ITEM_FIELDS))).encode('ascii', 'ignore') + '\n'
    for x in zipped:
        ret += print_issue_summary(x[0], date_days_range_start)
    return ret


if __name__ == "__main__":
    print query('project = "CNN Android Titan Project" and assignee = swei and status != Done and status != QA order by updated desc')
