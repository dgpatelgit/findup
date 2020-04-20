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