import bs4
import requests as re
import mysql.connector
import urllib.request as ure
import boto3
from botocore.client import Config
import os

class getCompaniesInfo():
    def chkDuplicat(cname, nttype):
        mydb = mysql.connector.connect(
            host="database-2.crigucvmj05t.eu-west-2.rds.amazonaws.com",
            user="admin",
            passwd="GPx90NKU4WlTTHB8PEb3",
            database="insolvency"
        )
        mdb = mydb
        mycursor = mdb.cursor()

        mycursor.execute("SELECT * FROM craditors_companies WHERE `company_name` = '"+cname+"' AND `notice_type` = '"+nttype+"' ")
        mycursor.fetchall()

        num_row = mycursor.rowcount

        return num_row    

    def scrapeTheGazette(areacode):
        headers = {"User-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
        url = "https://www.thegazette.co.uk/insolvency/notice?results-page-size=100&numberOfLocationSearches=1&location-distance-1=1&categorycode=G405010101+G405010102+G405010103+-2&service=insolvency&location-postcode-1="+areacode
        data = re.get(url,headers=headers)
        soup = bs4.BeautifulSoup(data.text, 'html.parser')

        mainSection = soup.find("div", {"class":"main-pane"})
        numNotice = mainSection.find("p", {"class":"number-notices"}).text
        if numNotice == ' You have got 0 results ':
            pass
        else:    
            ttlNum = int(numNotice.split('of')[1].split(' ')[1])
            ttlPage = int(ttlNum/100)

            mydb = mysql.connector.connect(
                host="database-2.crigucvmj05t.eu-west-2.rds.amazonaws.com",
                user="admin",
                passwd="GPx90NKU4WlTTHB8PEb3",
                database="insolvency"
            )
            mycursor = mydb.cursor()

            compDict = []

            if ttlPage == 0:
                #mainContent = mainSection.find("div", {"class":"content"})
                for content in mainSection.find_all("div", {"class":"feed-item"}):
                    title = content.find("h3", {"class":"title"})
                    company_name = title.text

                    pub_date = content.find("dl", {"class":"publication-date"})
                    notice_date = pub_date.find("time")
                    if notice_date == None:
                        notice_date = ''
                    else:
                        notice_date = notice_date.text

                    nttype = content.find("dl", {"class":"notice-type"}).find("dd")
                    if nttype == None:
                        nttype = ''
                    else:
                        nttype = nttype.text

                    link = title.find("a")['href']

                    companyUrl = 'https://www.thegazette.co.uk'+link

                    companyData = re.get(companyUrl, headers=headers)
                    companySoup = bs4.BeautifulSoup(companyData.text, 'html.parser')

                    notice_id = companySoup.find("dd", {"property":"gaz:hasNoticeID"})
                    if notice_id == None:
                        notice_id = ''
                    else:
                        notice_id = notice_id.text

                    Administrator = companySoup.find("p", {"data-gazettes":"Administrator"})
                    if Administrator == None:
                        Administrator = ''
                    else:
                        Administrator = Administrator.text.replace('\n', '').strip()

                    DateOfAppointment = companySoup.find("span", {"data-gazettes":"DateOfAppointment"})
                    if DateOfAppointment == None:
                        DateOfAppointment = ''
                    else:
                        DateOfAppointment = DateOfAppointment.text

                    CourtNumber = companySoup.find("span", {"property":"caseCode"})
                    if CourtNumber == None:
                        CourtNumber = ''
                    else:
                        CourtNumber = CourtNumber.text    
                    companyNumber = companySoup.find("span", {"data-gazettes":"CompanyNumber"})
                    if companyNumber == None:
                        companyNumber = ''
                    else:
                        companyNumber = companyNumber.text

                    compList = (companyNumber, str(company_name), str(areacode), str(Administrator), str(CourtNumber), str(DateOfAppointment), notice_id, str(nttype), str(notice_date))

                    compDict.append(compList)
            else:
                for i in range(ttlPage+1):
                    page_num = i+1
                    url += '&results-page='+str(page_num)
                    data = re.get(url,headers=headers)
                    subsoup = bs4.BeautifulSoup(data.text, 'html.parser')
                    mainSection = subsoup.find("div", {"class":"main-pane"})
                    
                    for content in mainSection.find_all("div", {"class":"feed-item"}):
                        title = content.find("h3", {"class":"title"})
                        company_name = title.text

                        pub_date = content.find("dl", {"class":"publication-date"})
                        notice_date = pub_date.find("time")
                        if notice_date == None:
                            notice_date = ''
                        else:
                            notice_date = notice_date.text

                        nttype = content.find("dl", {"class":"notice-type"}).find("dd")
                        if nttype == None:
                            nttype = ''
                        else:
                            nttype = nttype.text

                        link = title.find("a")['href']   

                        companyUrl = 'https://www.thegazette.co.uk'+link

                        companyData = re.get(companyUrl, headers=headers)
                        companySoup = bs4.BeautifulSoup(companyData.text, 'html.parser')

                        notice_id = companySoup.find("dd", {"property":"gaz:hasNoticeID"})
                        if notice_id == None:
                            notice_id = ''
                        else:
                            notice_id = notice_id.text

                        Administrator = companySoup.find("p", {"data-gazettes":"Administrator"})
                        if Administrator == None:
                            Administrator = ''
                        else:
                            Administrator = Administrator.text.replace('\n', '').strip()

                        DateOfAppointment = companySoup.find("span", {"data-gazettes":"DateOfAppointment"})
                        if DateOfAppointment == None:
                            DateOfAppointment = ''
                        else:
                            DateOfAppointment = DateOfAppointment.text

                        CourtNumber = companySoup.find("span", {"property":"court:caseCode"})
                        if CourtNumber == None:
                            CourtNumber = ''
                        else:
                            CourtNumber = CourtNumber.text    
                        companyNumber = companySoup.find("span", {"data-gazettes":"CompanyNumber"})
                        if companyNumber == None:
                            companyNumber = ''
                        else:
                            companyNumber = companyNumber.text

                        compList = (companyNumber, str(company_name), str(areacode), str(Administrator), str(CourtNumber), str(DateOfAppointment), notice_id, str(nttype), str(notice_date))

                        compDict.append(compList)                    

            rows = ''
            for i in range(len(compDict) - 1):
                cname = compDict[i][1]
                cnttp = compDict[i][7]

                chknumrow = getCompaniesInfo.chkDuplicat(cname, cnttp)

                if chknumrow > 0:
                    pass
                else:
                    rows += "(Null,'{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(compDict[i][0], compDict[i][1], compDict[i][2], compDict[i][3], compDict[i][4], compDict[i][5], compDict[i][6], compDict[i][7], compDict[i][8])
                    if i != len(compDict) - 2:
                        rows += ','

            SQL = "INSERT INTO `craditors_companies` VALUES " + rows

            try:
                mycursor.execute(SQL)
                mydb.commit()
            except:
                mydb.rollback()

            mydb.close()        
            
    def runGetCompanies():
        mydb = mysql.connector.connect(
            host="database-2.crigucvmj05t.eu-west-2.rds.amazonaws.com",
            user="admin",
            passwd="GPx90NKU4WlTTHB8PEb3",
            database="insolvency"
        )
        mdb = mydb
        mycursor = mdb.cursor()

        mycursor.execute("SELECT * FROM `craditors_codes`")

        for row in mycursor.fetchall():
            pscode = row[1]
            getCompaniesInfo.scrapeTheGazette(pscode)

class getAdminProposal:
    def uPloadFile(file):
        ACCESS_KEY_ID = 'AKIATSEAQZOYLVVZMUVN'
        ACCESS_SECRET_KEY = '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'
        BUCKET_NAME = 'insolvency-admin-proposal-bucket'
        FILE_NAME = file

        data = open(FILE_NAME, 'rb')

        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

        s3.Bucket(BUCKET_NAME).put_object(Key=FILE_NAME, Body=data, ACL='public-read')

    def downLoadPDF(url, file_name):
        headers = {"User-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
        data = re.get(url,headers=headers)

        s3url = data.url

        ure.urlretrieve(s3url, file_name) #'inserted-company-3-5.pdf'

        getAdminProposal.uPloadFile(file_name)

        os.remove(file_name)

    def insertToDB(number, name, link):
        mydb = mysql.connector.connect(
            host="database-2.crigucvmj05t.eu-west-2.rds.amazonaws.com",
            user="admin",
            passwd="GPx90NKU4WlTTHB8PEb3",
            database="insolvency"
        )
        mycursor = mydb.cursor()

        #rows = "(NULL, '{}', '{}', '{}')".format(number, name, link)

        sql = "INSERT INTO `craditors_admin_proposal` (`id`, `company_number`, `admin_proposal_name`, `admin_proposal_link`) VALUES (NULL, '"+number+"', '"+name+"', '"+link+"')"

        mycursor.execute(sql)
        mydb.commit()        

    def getBetaHouse(company_number):
        headers = {"User-agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
        company_number = str(company_number)
        url  = 'https://beta.companieshouse.gov.uk/company/'+company_number+'/filing-history'
        data = re.get(url,headers=headers)
        soup = bs4.BeautifulSoup(data.text, 'html.parser')

        num_page = len(soup.find_all("a", {"class":"page"}))
        
        for i in range(num_page):
            if i == 0:
                pass
            else:
                url  = 'https://beta.companieshouse.gov.uk/company/'+company_number+'/filing-history?page='+str(i)
                data = re.get(url,headers=headers)
                soup = bs4.BeautifulSoup(data.text, 'html.parser')
                tbody  = soup.find("table", {"class":"full-width-table"})

                for tr in tbody.find_all("tr"):
                    trtxt = tr.text
                    if (trtxt.find("Statement of administrator's proposal") != -1 or trtxt.find("Notice of administrator's proposal") != -1):
                        download = tr.find("a", {"class":"download"})
                        dl_link = 'https://beta.companieshouse.gov.uk'+download['href']
                        tr_ttl = tr.find('strong').text.replace("'", "")

                        file_name = 'cmp_'+company_number+'_'+tr_ttl+'.pdf'
                        file_link = 'https://insolvency-admin-proposal-bucket.s3-us-west-2.amazonaws.com/'+file_name
                        #print(file_link)
                        #print(file_name)
                        getAdminProposal.downLoadPDF(dl_link,file_name)
                        getAdminProposal.insertToDB(company_number, file_name, file_link)
                    else:
                        pass

    def runGetProposal():
        mydb = mysql.connector.connect(
            host="database-2.crigucvmj05t.eu-west-2.rds.amazonaws.com",
            user="admin",
            passwd="GPx90NKU4WlTTHB8PEb3",
            database="insolvency"
        )
        mdb = mydb
        mycursor = mdb.cursor()

        mycursor.execute("SELECT * FROM `craditors_companies`")

        for row in mycursor.fetchall():
            cmp_num = row[1]
            getAdminProposal.getBetaHouse(cmp_num)                        

#getAdminProposal.getBetaHouse('02603357')
#getAdminProposal.runGetProposal()
#getAdminProposal.insertToDB('16235267', 'beta house ajsjak', 'https://beta.companieshouse.gov.uk/company/02603357/filing-history/MzIzNTk1MzA2NmFkaXF6a2N4/document?format=pdf&download=0')
#getAdminProposal.downLoadPDF('https://beta.companieshouse.gov.uk/company/02603357/filing-history/MzIzNTk1MzA2NmFkaXF6a2N4/document?format=pdf&download=0')
#getCompaniesInfo.scrapeTheGazette('LL41')
#getCompaniesInfo.runGetCompanies()      
#getCompaniesInfo.chkDuplicat("WASTECHNIQUE LIMITED", "Appointment of Administrators")