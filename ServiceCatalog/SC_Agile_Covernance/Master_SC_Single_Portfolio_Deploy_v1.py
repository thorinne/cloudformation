#!/usr/bin/python
"""
Automate the build of Service Catalog Portfolio, Products and Template Constraints in Master account
"""
###############
#Create Template definitions
###############
import boto3
import random
import time
import sys

sc_client = boto3.client('servicecatalog', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')

rgn = 'us-east-1' #Region to Deploy
linux_portfolio = 'Master Linux Portfolio' #Name of Master Linux Portfolio
linux_lamp_constraint_description ='Linux LAMP Template Constraint'
linux_instance_constraint_description ='Linux Instance Template Constraint'
linux_product_name = []
linux_product_id = []

# share_account = sys.argv[1:] #Get Argument Passed on Command Line for Accounts to share with

#Random tokens to use for IdempotencyToken value in Portfolio and Product Deployment
token = "token"+str(int(random.random()*1000000))
token2 = "token2"+str(int(random.random()*1000000))
token3 = "token3"+str(int(random.random()*1000000))
token4 = "token4"+str(int(random.random()*1000000))

###############
#Custom Variables Edit these to fir your deployment
###############

bucket = ''
share_account =''
if len(sys.argv) > 1:
    bucket = sys.argv[1]
    share_account = sys.argv[2:]
else:
    print("Please specifiy bucket that the CloudFormation and Constraint templates are in.")
    exit()

# bucket = 'jsnorcode'
master_key = 'LAMP_Launch_Constraint.json' #Master Constraint Key
instance_key = 'Linux_Instance_Launch_Constraint.json' #Instance Constraint Key
linux_portfolio = 'Master Linux Portfolio'


LinuxStackTemplateURL= 'https://s3.amazonaws.com/'+bucket+'/LAMP_Single_Instance_v1.template'
LinuxInstanceTemplateURL= 'https://s3.amazonaws.com/'+bucket+'/Linux_Single_Instance_v1.template'

print ("\n")
print ("################Creating Linux Portfolio and Products################")
print ("\n")

###############
#Create Master Linux Portfolio
###############
response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
name = [ x['DisplayName'] for x in response['PortfolioDetails'] ]
print ("Your list of Service Catalog Portfolio's are:")
print (name)
print ("\n")
if linux_portfolio not in name:
    try:
        response = sc_client.create_portfolio(
            AcceptLanguage='en',
            DisplayName=linux_portfolio,
            Description='Master Linux Portfolio which builds the LAMP stack and Single Linux instance ',
            ProviderName='IT Services',
            Tags=[
                {
                    'Key': 'Portfolio',
                    'Value': linux_portfolio
                },
            ],
            IdempotencyToken = token2
        )
        print ("Creating Portfolio")
        time.sleep(10)
    except:
        print ("Error creating Linux Portfolio " +linux_portfolio)
        pass

if linux_portfolio in name:
    print ("Your Linux Portfolio " +linux_portfolio+ " already exists")
###############
#Search for Linux LAMP Stack product and get ProductId
###############
try:
    linux_product_search = sc_client.search_products_as_admin(
        AcceptLanguage='en',
        Filters={
            'FullTextSearch': [
                'Linux LAMP Stack',
            ]
        },
        PageSize=20,
        SortBy='Title',
        SortOrder='ASCENDING'
    )
    linux_product_name = linux_product_search['ProductViewDetails'][0]['ProductViewSummary']['Name']
    linux_product_id = linux_product_search['ProductViewDetails'][0]['ProductViewSummary']['ProductId']
    if linux_product_name != 'Linux LAMP Stack':
        linux_product_name = []
        linux_product_id = []
        print ("Your Linux product name is: " +linux_product_name)
        print ("Your Linux Product Id is: " +linux_product_id)
except:
    print ("Linux Product Not Found")
    pass

###############
#If Linux LAMP Stack product not found create
###############

if linux_product_name == 'Linux LAMP Stack':
    print ("Linux Product " +linux_product_name+ " already exists")
if linux_product_name != 'Linux LAMP Stack':
    try:
        sc_client.create_product(
            AcceptLanguage='en',
            Name='Linux LAMP Stack',
            Owner='IT Services',
            Description='Linux LAMP stack that builds the Apache web server, PHP and MySQL database',
            Distributor='IT Services',
            SupportDescription='Operations Team',
            SupportEmail='support@company.com',
            SupportUrl='http://helpdesk.company.com',
            ProductType='CLOUD_FORMATION_TEMPLATE',
            Tags=[
                {
                    'Key': 'ProductName',
                    'Value': 'Linux LAMP Stack'
                },
            ],
            ProvisioningArtifactParameters={
                'Name': 'Linux LAMP Stack',
                'Description': 'Linux LAMP stack that builds the Apache web server, PHP and MySQL database',
                'Info': {
                    'LoadTemplateFromURL': LinuxBaselineTemplateURL
                },
                'Type': 'CLOUD_FORMATION_TEMPLATE'
            },
            IdempotencyToken=token2
        )
        print ("Creating LAMP Stack Product")
        time.sleep(10)
    except:
        print ("Linux Product already exists or error creating product Linux LAMP Stack")


if linux_product_name != 'Linux LAMP Stack':
    try:
        linux_product_search = sc_client.search_products_as_admin(
            AcceptLanguage='en',
            Filters={
                'FullTextSearch': [
                    'Linux LAMP Stack',
                ]
            },
            PageSize=20,
            SortBy='Title',
            SortOrder='ASCENDING'
        )
        linux_product_name = linux_product_search['ProductViewDetails'][0]['ProductViewSummary']['Name']
        linux_product_id = linux_product_search['ProductViewDetails'][0]['ProductViewSummary']['ProductId']
        print ("Your Linux LAMP Stack product name is: " +linux_product_name)
        print ("Your Linux LAMP Stack Product Id is: " +linux_product_id)
        if linux_product_name != 'Linux LAMP Stack':
            linux_product_name = []
            linux_product_id = []
    except:
        print ("Linux Product Not Found")
        pass

###############
#Get Master Linux Portfolio and PortfolioId and associate Linux LAMP Stack Product with Linux Portfolio
###############
linux_pf_id = []
linux_portfolio_id = []
try:
    response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details if x['DisplayName'] == 'Master Linux Portfolio']
    linux_pf_id = str(ID)[3:-2]
    print ("Your Linux Portfolio ID is: " +linux_pf_id)
except:
    print ("Error getting Master Linux Portfolio Id")
    pass
try:
    linux_porfolio_list = sc_client.list_portfolios_for_product(
        AcceptLanguage='en',
        ProductId=linux_product_id,
        PageSize=20
    )
    linux_portfolio_id = linux_porfolio_list['PortfolioDetails'][0]['Id']
    print ("Your associated Portfolio's for Linux LAMP Stack is " +str(linux_portfolio_id))
except:
    print ("Your Linux LAMP Stack is not associated with a Portfolio")
    pass
if linux_pf_id != linux_portfolio_id:
    try:
        response = sc_client.associate_product_with_portfolio(
            AcceptLanguage='en',
            ProductId=linux_product_id,
            PortfolioId=linux_pf_id
        )
        print ("Associating LAMP product with Portfolio")
        time.sleep(5)
    except:
        print ("Error associating " +str(linux_product_name)+ " with portfolio " +str(linux_portfolio))
        pass



###############
#Create Template constraint for Master Linux LAMP Stack Portfolio
###############
cs_description = []
try:
    response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details if x['DisplayName'] == 'Master Linux Portfolio']
    linux_pf_id = str(ID)[3:-2]
    print ("Your Linux Portfolio ID is: " +linux_pf_id)
except:
    print ("Error getting Master Linux Portfolio Id")
    pass
if linux_pf_id != []:
    try:
        constraints = sc_client.list_constraints_for_portfolio(
        AcceptLanguage='en',
        PortfolioId=linux_pf_id,
        ProductId=linux_product_id,
        PageSize=20
    )
        cs_description = constraints['ConstraintDetails'][0]['Description']
    except:
        print ("Error getting Linux Constraint description")
        pass
    if cs_description != linux_lamp_constraint_description:
        get_constraint = s3_client.get_object(Bucket=bucket, Key=master_key)
        read_constraint = get_constraint['Body'].read().decode('utf-8')
        try:
            response = sc_client.create_constraint(
                AcceptLanguage='en',
                PortfolioId=linux_pf_id,
                ProductId=linux_product_id,
                Parameters = read_constraint,
                Type='TEMPLATE',
                Description=linux_lamp_constraint_description,
                IdempotencyToken = token2
            )
            print ("Creating LAMP Template Constraint")
            time.sleep(5)        
        except:
            print ("Error Creating Contraint for " +linux_portfolio)
            pass



###############
#Search for Linux Instance product and get ProductId
###############
try:
    linux_inst_product_search = sc_client.search_products_as_admin(
        AcceptLanguage='en',
        Filters={
            'FullTextSearch': [
                'Linux Instance',
            ]
        },
        PageSize=20,
        SortBy='Title',
        SortOrder='ASCENDING'
    )
    linux_inst_product_name = linux_inst_product_search['ProductViewDetails'][0]['ProductViewSummary']['Name']
    linux_inst_product_id = linux_inst_product_search['ProductViewDetails'][0]['ProductViewSummary']['ProductId']
    if linux_inst_product_name != 'Linux Instance':
        linux_inst_product_name = []
        linux_inst_product_id = []
        print ("Your Linux product name is: " +linux_inst_product_name)
        print ("Your Linux Product Id is: " +linux_inst_product_id)
except:
    print ("Linux Product Not Found")
    pass

###############
#If Linux Instance product not found create
###############

if linux_inst_product_name == 'Linux Instance':
    print ("Linux Product " +linux_inst_product_name+ " already exists")
if linux_inst_product_name != 'Linux Instance':
    try:
        sc_client.create_product(
            AcceptLanguage='en',
            Name='Linux Instance',
            Owner='IT Services',
            Description='Single Linux Instance to add behind the WebASG Security Group',
            Distributor='IT Services',
            SupportDescription='Operations Team',
            SupportEmail='support@company.com',
            SupportUrl='http://helpdesk.company.com',
            ProductType='CLOUD_FORMATION_TEMPLATE',
            Tags=[
                {
                    'Key': 'ProductName',
                    'Value': 'Linux LAMP Stack'
                },
            ],
            ProvisioningArtifactParameters={
                'Name': 'Linux Instance',
                'Description': 'Single Linux Instance to add behind the WebASG Security Group',
                'Info': {
                    'LoadTemplateFromURL': LinuxInstanceTemplateURL
                },
                'Type': 'CLOUD_FORMATION_TEMPLATE'
            },
            IdempotencyToken=token4
        )
        print ("Creating Linux Instance Product")
        time.sleep(10)
    except:
        print ("Linux Product already exists or error creating product Linux Instance")

if linux_inst_product_name != 'Linux Instance':
    try:
        linux_inst_product_search = sc_client.search_products_as_admin(
            AcceptLanguage='en',
            Filters={
                'FullTextSearch': [
                    'Linux Instance',
                ]
            },
            PageSize=20,
            SortBy='Title',
            SortOrder='ASCENDING'
        )
        linux_inst_product_name = linux_inst_product_search['ProductViewDetails'][0]['ProductViewSummary']['Name']
        linux_inst_product_id = linux_inst_product_search['ProductViewDetails'][0]['ProductViewSummary']['ProductId']
        print ("Your Linux Instance product name is: " +linux_inst_product_name)
        print ("Your Linux Instance Product Id is: " +linux_inst_product_id)
        if linux_inst_product_name != 'Linux Instance':
            linux_inst_product_name = []
            linux_inst_product_id = []
    except:
        print ("Linux Product Not Found")
        pass

###############
#Get Master Linux Portfolio and PortfolioId and associate Linux Instance Product
###############
linux_inst_pf_id = []
linux_portfolio_id = []
try:
    response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details if x['DisplayName'] == 'Master Linux Portfolio']
    linux_inst_pf_id = str(ID)[3:-2]
    print ("Your Linux Portfolio ID is: " +linux_inst_pf_id)
except:
    print ("Error getting Master Linux Portfolio Id")
    pass
try:
    linux_inst_porfolio_list = sc_client.list_portfolios_for_product(
        AcceptLanguage='en',
        ProductId=linux_inst_product_id,
        PageSize=20
    )
    linux_portfolio_id = linux_inst_porfolio_list['PortfolioDetails'][0]['Id']
    print ("Your associated Portfolio's for Linux Instance is " +str(linux_portfolio_id))
except:
    print ("Your Linux Instance is not associated with a Portfolio")
    pass
if linux_inst_pf_id != linux_portfolio_id:
    try:
        response = sc_client.associate_product_with_portfolio(
            AcceptLanguage='en',
            ProductId=linux_inst_product_id,
            PortfolioId=linux_inst_pf_id
        )
        print ("Creating Linux Instance Template Constraint")
        time.sleep(5)
    except:
        print ("Error associating " +str(linux_inst_product_name)+ " with portfolio " +str(linux_portfolio))
        pass


###############
#Create Template constraint for Master Linux Instance Portfolio
###############
cs_description = []
try:
    response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details if x['DisplayName'] == 'Master Linux Portfolio']
    linux_inst_pf_id = str(ID)[3:-2]
    print ("Your Linux Portfolio ID is: " +linux_inst_pf_id)
except:
    print ("Error getting Master Linux Portfolio Id")
    pass
if linux_inst_pf_id != []:
    try:
        constraints = sc_client.list_constraints_for_portfolio(
        AcceptLanguage='en',
        PortfolioId=linux_inst_pf_id,
        ProductId=linux_inst_product_id,
        PageSize=20
    )
        cs_description = constraints['ConstraintDetails'][0]['Description']
    except:
        "Error getting Linux Constraint description"
        pass
    if cs_description != linux_instance_constraint_description:
        get_constraint = s3_client.get_object(Bucket=bucket, Key=instance_key)
        read_constraint = get_constraint['Body'].read().decode('utf-8')
        try:
            response = sc_client.create_constraint(
                AcceptLanguage='en',
                PortfolioId=linux_inst_pf_id,
                ProductId=linux_inst_product_id,
                Parameters = read_constraint,
                Type='TEMPLATE',
                Description=linux_instance_constraint_description,
                IdempotencyToken = token4
            )
            print ("Creating Linux Instance Template Constraint")
            time.sleep(5)
        except:
            print ("Error Creating Contraint for " +linux_portfolio)
            pass
            


print ("\n")
print ("################Sharing Portfolio(s) with Child Accounts################")
print ("##########Your Account List is: " +str(share_account)+ " ##########")
print ("\n")

###############
#Share Windows Portfolio with Child Account(s)
###############

for x in share_account:
    try:
        sc_client.create_portfolio_share(
            AcceptLanguage='en',
            PortfolioId=windows_pf_id,
            AccountId=x
        )
        print ("Master Windows Portfolio shared with account " +x)
    except:
        print ("Error sharing Master Windows Portfolio with account " +x)
        pass


###############
#Share Linux Portfolio with Child Account(s)
###############

for x in share_account:
    try:
        sc_client.create_portfolio_share(
            AcceptLanguage='en',
            PortfolioId=linux_pf_id,
            AccountId=x
        )
        print ("Master Linux Portfolio shared with account " +x)
    except:
        print ("Error sharing Master Linux Portfolio with account " +x)
        pass

