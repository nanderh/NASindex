#For now the code is a little bit messy and it outputs almost everything it does to make debugging a bit easier.
#And the subprocess call with shell is not very secure but it is for now the only way to run curl


import MySQLdb
import shodan
import subprocess
import time

#shodan api key
API_KEY = "[SHODAN API KEY HERE]"

#this is the default query to find iomega servers
SHODAN_SEARCH_QUERY = "iomega 200"

#Create database connection
def create_database_connection():
    try:
        print "[+] %s - Creating database connection..." % time.strftime("%c")
        global db
        global cursor
        db = MySQLdb.connect("[DATABASE IP ADDRESS]","[DATABASE USERNAME]","[DATABASE PASSWORD]","[DATABASE NAME]" )
        cursor = db.cursor()
        print "[+] %s - Created database connection" % time.strftime("%c")
    except MySQLdb.Error, e:
        print "[+] %s - Got database error %s" % (time.strftime("%c"), e)
        print "[+] %s - Exiting!..." % time.strftime("%c")
        exit()

def fetch_shodan_results():
    print "[+] %s - Searching Shodan..." % time.strftime("%c")
    api = shodan.Shodan(API_KEY)
    results = api.search(SHODAN_SEARCH_QUERY)
    return results

def check_if_live(ip,port):
    #initialize command var
    command = None
    #based on the port we either use https or http for curl
    if ( port == "443" ) or ( port == "445" ):
        print "Doing https"
        command = 'timeout 2s curl -I -k -s --connect-timeout 1 https://%s/' % ip
    if port == "80":
        print "Doing http"
        command = 'timeout 2s curl -I -k -s --connect-timeout 1 http://%s/' % ip
        
    print command
    #if command is successfully created
    if command != None:
        try:
            #run the command with subprocess
            header = subprocess.check_output(command, shell=True)
            #split the header into lines and loop through
            for line in header.splitlines():
                #iomega header contains "Set-Cookie"
                if "Set-Cookie: iomega" in line:
                    return True
                
        except subprocess.CalledProcessError as e:
            print "[+] %s - Got an error executing curl: %s" % (time.strftime("%c"), e)
            return False
        
    #if command is not successfully created then return none
    if command == None:
        return False

def cross_reference_db(local_ip,port,country):
    #query the db based on ip
    sql = "SELECT * FROM server_ids WHERE ip='%s'" % ip
    cursor.execute(sql)
    cross_reference_result = cursor.fetchone()
          
    #if no result is returned then we create a new entry
    if cross_reference_result == None:
        print "[+] %s - Got a new server, committing to db: %s" % (time.strftime("%c"), local_ip)
        query = "INSERT INTO server_ids(ip, country, port) VALUES ('%s', '%s', '%s')" % (local_ip, country, port)
        commit_to_db(query)
        
    if cross_reference_result != None:
        print "[+] %s - IP is already in db, ignoring: %s" % (time.strftime("%c"), local_ip)

def commit_to_db(query):
    try:
        cursor.execute(query)
        db.commit()                   
    except MySQLdb.Error, e:
        db.rollback()               
        print "[+] %s - Got database error: %s" % (time.strftime("%c"), e)
        pass

if __name__ == "__main__":
    
    #connect to the database
    create_database_connection()
    
    #get the results from shodan
    results = fetch_shodan_results()
    
    #loop through the results
    for result in results['matches']:
        #store the vars locally
        ip = result['ip_str']
        country = result['location']['country_code']
        port = str(result['port'])
        print "Doing %s, %s, %s" % (ip, port, country)
        #check whether live
        if check_if_live(ip,port) == True:
        ##the cross reference function will handle whether to create a new entry or ignore it
            cross_reference_db(ip,port,country)
            
    db.close()
    exit()
        
        
        
        