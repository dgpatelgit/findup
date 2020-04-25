import time
import locale

class WebUIHelper:
  def __init__(self):
    locale.setlocale(locale.LC_ALL, '')

  def getHTMLHeader(self):
    """
    Function gets the header of the html response
    """
    return '''
    <html>
      <head>
          <title>Findup</title>
      </head>
      <body>
          <center>
            <br/><h2>Welcome to Findup</h2>
            <hr/>
            <input type="button" value="HOME" onClick="window.location.href='/'">
            <input type="button" value="NEW SCAN" onClick="window.location.href='/scan/new'">
            <hr/>
    '''

  def getHTMLFooter(self):
    """
    Function gets the footer data of the html page.
    """
    return '''
          </center>
        </body>
    </html>
    '''

  def getHTMLPage(self, content):
    """
    Function returns HTML page with given content
    """
    return self.getHTMLHeader() + content + self.getHTMLFooter()

  def getReadableTimestamp(self, timestamp):
    return time.ctime(timestamp / 1000)

  def getReadableObjectSize(self, bytes, units=[' bytes',' Kb',' Mb',' Gb',' Tb', ' Pb', ' Eb']):
    """ Returns a human readable string reprentation of bytes"""
    return str(bytes) + units[0] if bytes < 1024 else self.getReadableObjectSize(bytes >> 10, units[1:])

  def getReadableNumber(self, n):
    return locale.format("%d", n, grouping = True)

  def getNewScanForm(self, scanName = "", message = None):
    htmlForm = '''
    <form id="formNewScan" name="formNewScan" action="/scan/new" method="POST" enctype="multipart/form-data">
      <table border="1" cellpadding="5" cellspacing="5">
        <tr>
          <td colspan="2"><center>CREATE A NEW SCAN</center></td>
        <tr>
    '''

    if message is not None:
      htmlForm += '''
        <tr>
          <td colspan="2"><center>{message}</center></td>
        <tr>
      '''.format(message=message)

    htmlForm += '''
        <tr>
          <td>Name</td>
          <td><input type="text" id="txtName" name="txtName" length="50" max-length="40" value="{scanName}" /></td>
        </tr>
        <tr>
          <td>Root Path</td>
          <td><input type="file" id="filePath" name="filePath" length="150" webkitdirectory=true value="" /></td>
        </tr>
        <tr>
          <td>&nbsp;</td>
          <td><input type="submit" value="SCAN" onClick="alert(document.getElementById('filePath').value)" /></td>
        </tr>
      </table>
    </form>
    '''.format(scanName=scanName)

    return htmlForm