import os
from bottle import get, post, request, run
from core.sqlite_db import DB
from core.scan import Scan
from webui.webui_helper import WebUIHelper

webuiHelper = WebUIHelper()


@get('/')
def scan_list():
    """
    Function that servers /scan/list, returns list of the current scans.
    It returns top 50 scans in descending order of their time i.e., latest scan comes on top.
    It displays information like scan name, path, state, created time, total folders and files.
    """
    scan = Scan()
    db = DB()
    query = """SELECT id, name, root_path, state, folder_count, file_count, total_size_in_bytes,
  created_timestamp FROM scan ORDER BY created_timestamp DESC"""
    scans = db.fetchAll(query, None)
    response = '''
    <table cellspacing="5" cellpadding="5" border="1">
      <tr>
        <td>Scan ID</td>
        <td>Name</td>
        <td>Root Path</td>
        <td>State</td>
        <td>Folder Count</td>
        <td>File Count</td>
        <td>Total Size</td>
        <td>Created</td>
      </tr>
  '''
    for s in scans:
        response += """
    <tr>
      <td>{scanId}</td>
      <td>{name}</td>
      <td>{rootPath}</td>
      <td>{state}</td>
      <td>{folderCount}</td>
      <td>{fileCount}</td>
      <td>{totalSize}</td>
      <td>{createdDateTime}</td>
    </tr>
    """.format(scanId=s[0], name=s[1], rootPath=s[2], state=scan.getReadableState(s[3]), folderCount=webuiHelper.getReadableNumber(s[4]),
               fileCount=webuiHelper.getReadableNumber(s[5]), totalSize=webuiHelper.getReadableObjectSize(s[6]), createdDateTime=webuiHelper.getReadableTimestamp(s[7]))
    response += "</table>"

    return webuiHelper.getHTMLPage(response)


@get('/scan/new')
def scan_new_get():
    """
    Function to server new scan request, it will be added to the list and core server will process it.
    """
    return webuiHelper.getHTMLPage(webuiHelper.getNewScanForm("", None))


@post('/scan/new')
def scan_new_post():
    """
    Function triggered by new scan form upon submit. This will place a new scan request in database.
    """
    scanName = request.forms.get("txtName") or None
    if scanName is None:
        return webuiHelper.getHTMLPage(webuiHelper.getNewScanForm("", "Missing scan name."))

    rootPath = request.files.get("filePath") or None
    if rootPath is None:
        return webuiHelper.getHTMLPage(webuiHelper.getNewScanForm(scanName, "Missing file name."))
    else:
        object_methods = [method_name for method_name in dir(
            rootPath) if not callable(getattr(rootPath, method_name))]
        return webuiHelper.getHTMLPage(webuiHelper.getNewScanForm("", "New scan request created successfully. {dt}".format(dt=rootPath.file.name)))

    return webuiHelper.getHTMLPage(webuiHelper.getNewScanForm("", "New scan request created successfully."))


run(host='localhost', port=8080, debug=True)
