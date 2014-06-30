#This is the second stage where it pulls the ip addresses from the database where the root_folders cell is empty and loads them with phantomjs
#On the folder_content.html page there is a tree with all the root folders, first it looks for the tree and then loops through it to get the name of each folder

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import MySQLdb


def create_database_connection():
    try:
        print "[+] Creating database connection..."
        global db
        global cursor
        db = MySQLdb.connect("[DATABASE IP ADDRESS]","[DATABASE USERNAME]","[DATABASE PASSWORD]","[DATABASE NAME]" )
        cursor = db.cursor()
    except MySQLdb.Error, e:
        print "[+] Got database error %s" % e
        print "[+] Exiting!..."
        exit()

def start_webdriver():
    try:
        print "[+] Starting webdriver..."
        global driver
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        
        #Set a browser user agent so we dont get identified as a crawler
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )
        
        #Allow ssl errors because the servers use a self signed certificate
        driver = webdriver.PhantomJS('./phantomjs',service_args=["--ignore-ssl-errors=true", "--load-images=false"],desired_capabilities=dcap)

    except:
        print "[+] Got error while starting webdriver:"
        raise

def test_database():
    try:
        print "[+] Testing database.."
        cursor.execute("SELECT * FROM server_ids")
        cursor.execute('INSERT INTO server_ids(ip,root_folders) VALUES ("1","1")')
        db.rollback()
        print "[+] Database is good!"
    except MySQLdb.Error, e:
        print "[+] Database is not good: [%s] exiting..." % e
        db.close()
        exit()
 
def crawl_page(url, ip_id):
    #initiate folder_names var
    folder_names = None
    #initiate is_first var to prevent double comma
    is_first = True
    try:
        driver.set_page_load_timeout(20)
        #open the url
        driver.get(url)
        #get all the spans
        spans = driver.find_elements_by_tag_name("span")
        #loop through spans
        for span in spans:
            #get their id
            span_id = span.get_attribute("id")
            #see if it contains the right string
            if "ui-dynatree-id" in span_id:
                #split the id string so were left with the correct folder name
                folder_name = span_id.split("-")[3]
                #filter out the root folder
                if not "root" in folder_name:
                    #see if first to prevent double comma in db
                    if is_first == False:
                        #append a comma
                        folder_name = "," + folder_name
                        #append the var
                        folder_names = folder_names + folder_name
                    #see if first to prevent double comma in db
                    if is_first == True:
                        #append the var
                        folder_names = folder_name
                        #switch the is_first var
                        is_first = False
    except:
        
        print "Got webdriver error, continueing..."
        pass
    
    
    #if folder_names has content, commit the data to the db
    try:
        
        if folder_names != None:
            print "Contains folder(s), saving to db..."
            cursor.execute("UPDATE server_ids SET root_folders = %s WHERE id = %s", (folder_names, ip_id))
            
        else:
            print "No folder(s) found"
            cursor.execute("UPDATE server_ids SET root_folders = 'None available' WHERE id = %s", (ip_id))
        
        db.commit()
    except MySQLdb.Error, e:
        db.rollback()
        
        print "[+] Got database error: %s" % e
        pass




def close():
    print "[+] All done, exiting!..."
    driver.quit()
    db.close()
    exit()
    

if __name__ == "__main__":
      
    create_database_connection()
    
    test_database()
    
    start_webdriver()
      
    cursor.execute("SELECT * FROM server_ids WHERE root_folders IS NULL")
    
    rows = cursor.fetchall()
    
    total = len(rows)
    
    counter = 1
    
    for row in rows:
        #select the right column
        ip_id = row[0]
        ip = row[1]
        country = row[2]
        port = row[3]
        
        print "[+] Now doing: %s:%s , Nr: %s out of: %s" % (ip ,port , str(counter) , str(total))
        
        #build the url based on port number
        url = None
        if port == "443":
            url = "https://" + ip + "/foldercontent.html"
        if port == "445":
            url = "https://" + ip + "/foldercontent.html"
        if port == "80":
            url = "http://" + ip + "/foldercontent.html"
        
        #send the url to crawl function if url is correctly created
        if url != None:
            crawl_page(url, ip_id)
        else:
            print "Not a valid url, skipping..."
        
        counter +=1
        
    close()
            
            
            

