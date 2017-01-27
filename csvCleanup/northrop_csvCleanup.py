#!/usr/bin/python
import time
import csv
import re
import sys
import companyinfo
from companyinfo import infofiller
import locations
from locations import parser
import clearances
from clearances import clearance as clear
from sys import argv
import datetime
import cleanTags
from cleanTags import cleanTag
#  clearance,description,title,reqid,loclink,location,clearanceAndJunk
#csvFile = 'csvWork.csv'
logFile = 'logfile'
csvFile = 'csvWork.csv'
outFile = 'csvFinal.csv'
clearance = ""
doneThis = {}
encoding = 'asciiClean/encodingHTML.csv'
LOG = open(logFile, 'w')

# Open up the encoding converter file
def dictGen(file):
  outDict = {}
  with open(file, 'rb') as filecsv:
    filedata=csv.reader(filecsv)
    for row in filedata:
      if (len(row) > 2):
        outDict[row[1]]=row[0]
  return outDict
    

cleanDict = dictGen(encoding)



# Open CSV output stream
logDate= datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
companyName = 'Northrop Grumman'
output = open('/home/jbaker/Desktop/'+companyName+'_'+logDate+'_'+outFile, 'wb')
output2 = open('/home/jbaker/Desktop/'+companyName+'_2_'+logDate+'_'+outFile, 'wb')
wr = csv.writer(output, quoting=csv.QUOTE_ALL)
wr2 = csv.writer(output2, quoting=csv.QUOTE_ALL)

csv.register_dialect(
  'mydialect',
  delimiter=',',
  quotechar='"',
  doublequote=True,
  skipinitialspace=True,
  lineterminator='\r\n',
  quoting=csv.QUOTE_MINIMAL)


wr.writerow(['title', 'apply_url', 'job_description', 'location', 'company_name', 'company_description', 'company_website', 'company_logo', 'company_facebook', 'company_twitter', 'company_linkedin', 'career_id', 'deployment', 'travel', 'job_lat', 'job_lon', 'company_benefits', 'job_category', 'clearance', 'keywords'])

wr2.writerow(['title', 'apply_url', 'job_description', 'location', 'company_name', 'company_description', 'company_website', 'company_logo', 'company_facebook', 'company_twitter', 'company_linkedin', 'career_id', 'deployment', 'travel', 'job_lat', 'job_lon', 'company_benefits', 'job_category', 'clearance', 'keywords'])

infoComp,infoDesc,infoSite,infoLogo,infoFace,infoTwit,infoLinked,infoBeni=companyinfo.infofiller(companyName)

def cleanupAsciiEncoding(stringIn):
  for k in cleanDict:
    stringIn = re.sub(k, cleanDict[k], stringIn)
  stringOut = re.sub('\!\*\!', '', stringIn)
  return stringOut


with open(csvFile, 'rb') as mycsv:
  data=csv.reader(mycsv, dialect='mydialect')
  for row in data:
    keyw   = ''
    keywordsLoc = ''
    job_c = 'UNKNOWN'
    #print row[0]
    totalData = re.split('\!\|\!', row[0])
    #for d in range(len(totalData)):
      #print str(d)+'.'+totalData[d]
    if len(totalData) > 40:
      title   = totalData[13]
      desc   =  totalData[30]+totalData[31]+totalData[32]+totalData[33]
      req     = totalData[9]
      travel  = totalData[28]
      loc     = totalData[18]
      page_url= totalData[12]
      clearance = totalData[24]
      #print title+'\n\t'+req+'\n\t'+loc+'\n\t'+page_url+'\n\t'+clear+'\n\t'+travel
      desc = cleanupAsciiEncoding(desc)
      page_url = cleanupAsciiEncoding(page_url)
      #Append the reqId to this link:
      appUrl = 'https://ngc.taleo.net/careersection/application.jss?type=1&lang=en&portal=2160420105&reqNo='+req
      desc = cleanTag(desc)
      title = re.sub('^\s+|\s+$', '',title)
      if re.match('location', loc):
        LOG.write("Skipping header field")
      elif len(desc) == 0:
        LOG.write("This one has an empty desc.")
      elif doneThis.has_key(req):
        LOG.write("Already done this crap...")
      else:
        doneThis[req] = "TRUE"
        # This is the final fix for REQ
        clearance,keywords = clear.clear(clearance)
        for i in keywords:
          keyw=keyw+' '+i
        keyw=re.sub('^ ','',keyw)
        if (re.search('International', loc)):
          #for d in range(len(totalData)):
            #print str(d)+'.'+totalData[d]
          print "This is the job in question: "+page_url+"\nThis is the job title listed: "+title + "\nThis is the location field listed: "+loc+"\n\n"
        loc,lat,lon,keywordsLoc = parser.loc(loc,"northrop")
        keyw = keyw + ' ' + keywordsLoc
        #print loc + ' ||||||||||||| THIS IS FUCKED UP ||||||||||||| ' + keywordsLoc
        if not re.match("None|^$", clearance):
          wr.writerow([title, appUrl, desc, loc, infoComp, infoDesc, infoSite, infoLogo, infoFace, infoTwit, infoLinked, req, 'UNKNOWN', travel, lat, lon, infoBeni, job_c, clearance, keyw])
    else:
      next

