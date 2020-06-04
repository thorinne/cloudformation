#!/usr/bin/python
"""
Automate the build of Shared Service Catalog Portfolio, Products and Template baseline_constraint in Child accounts
"""

# please note that I am not setting the AWS region in this code which means that it will default to the AWS region of my shell where I run this script from.
# you can specify the region in the client call by setting the region_name parameter/value to the appropriate AWS region

###############
#Create Template definitions
###############
import boto3
import random
import time
import sys

sc_client = boto3.client('servicecatalog', region_name='us-east-1')
iam_client = boto3.client('iam', region_name='us-east-1')
session_client = boto3.client('sts')
# import_portfolios = ['port-rx4vc3kthfxfw']
# linux_portfolio_id = 'port-rx4vc3kthfxfw'
application_name = 'Linux Application'
linux_portfolio = 'Linux Portfolio'
baseline_constraint_description ='LAMP Launch Constraint'
instance_constraint_description ='LinuxInstance Launch Constraint'
linux_lamp_name = []
linux_lamp_id = []
linux_instance_name = []
linux_instance_id = []

token = "token"+str(int(random.random()*1000000))
token2 = "token2"+str(int(random.random()*1000000))
token3 = "token3"+str(int(random.random()*1000000))
token4 = "token4"+str(int(random.random()*1000000))

import_portfolios = ''
if len(sys.argv) > 1:
    import_portfolios = sys.argv[1]
else:
    print("Please enter the Portfolio Id generated from the Master Portfolio Deployment script ")
    exit()

linux_portfolio_id = import_portfolios
account_id = boto3.client('sts').get_caller_identity()['Account']
print("Yor account id is: " +account_id)



scfulluser_arn = 'arn:aws:iam::aws:policy/ServiceCatalogEndUserFullAccess'

def create_policy_arn( policy_name, policy_document, policy_description):
    client = boto3.client('iam')
    response = client.create_policy( PolicyName=policy_name, Path='/', PolicyDocument=policy_document, Description=policy_description)
    policy = {}
    policy = response['Policy']
    policy_arn = policy['Arn']
    return policy_arn


def create_roles(role_name, policy_arn):

    sc_policy = '{                                  \
            "Version": "2012-10-17",                \
            "Statement": [                          \
            {                                       \
                "Sid": "",                          \
                "Effect": "Allow",                  \
                "Principal": {                      \
                    "Service": "servicecatalog.amazonaws.com"       \
                },                                  \
            "Action": "sts:AssumeRole"              \
            }                                       \
            ]                                       \
        }'
    client = boto3.client('iam')
    response = client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=sc_policy
    )

    role_arn = response['Role']['Arn']
    iam = boto3.resource('iam')
    role = iam.Role(role_name)


    response = role.attach_policy(PolicyArn=policy_arn)
    return role_arn

def attach_policy_to_role(role_name, policy_arn):
    iam = boto3.resource('iam')
    role = iam.Role(role_name)

    response = role.attach_policy(PolicyArn=policy_arn)

print("################Importing Master Portfolio's, Creating Local Portfolio's and adding Products, Roles and Tags################")

###############
#Import Master Portfolios from import_portfolios list
###############
imported_portfolio_ids = []
try:
    response = sc_client.list_accepted_portfolio_shares(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details]
    imported_portfolio_ids = str(ID)
    print("Your Accepted Portfolio Shares are: " +imported_portfolio_ids)
except:
    print("Error getting Portfolio Id")
    pass
if import_portfolios not in imported_portfolio_ids:
	response = sc_client.accept_portfolio_share(
	    AcceptLanguage='en',
	    PortfolioId=import_portfolios
	)
	print("Portfolio " +import_portfolios+ "imported successfully.")
	# except:
	# 	print("Error importing portfolio " +x)
	# 	pass
###############
#Create a local portfolio to add shared Products from Master Portfolio
###############

response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
linux_name = [ x['DisplayName'] for x in response['PortfolioDetails'] ]
print("Your list of Service Catalog Portfolio's are:")
print(linux_name)
print("\n")
if linux_portfolio not in linux_name:
    try:
        print("Creating your Child Account Local Portfolio...")
        response = sc_client.create_portfolio(
            AcceptLanguage='en',
            DisplayName='Linux Portfolio',
            Description='Linux Portfolio which builds the LAMP stack and Single Linux instance',
            ProviderName='IT Services',
            Tags=[
                {
                    'Key': 'SC_Portfolio',
                    'Value': 'Linux Portfolio'
                },
            ],
            IdempotencyToken = token2
        )
        time.sleep(5)
    except:
        print("Error creating Linux Portfolio " +linux_portfolio)
        pass


if linux_portfolio in linux_name:
    print("Your Linux Portfolio " +linux_portfolio+ " already exists")

###############
#Search for Linux products and get ProductId
###############
linux_baseline_search = sc_client.search_products_as_admin(
    AcceptLanguage='en',
    PortfolioId=linux_portfolio_id,
    Filters={
        'FullTextSearch': [
            'Linux LAMP Stack',
        ]
    },
    PageSize=20,
    SortBy='Title',
    SortOrder='ASCENDING'
)
for product in linux_baseline_search['ProductViewDetails']:
    linux_lamp_name = product['ProductViewSummary']['Name']
    if linux_lamp_name == 'Linux LAMP Stack':
        linux_lamp_name = product['ProductViewSummary']['Name']
        linux_lamp_id = product['ProductViewSummary']['ProductId']
        print ("Your LAMP product name is: " +str(linux_lamp_name))
        print ("Your LAMP Product Id is: " +str(linux_lamp_id))
        break
if linux_lamp_name != 'Linux LAMP Stack':
    print ("Your Linux LAMP product was not found")

linux_instance_search = sc_client.search_products_as_admin(
    AcceptLanguage='en',
    PortfolioId=linux_portfolio_id,
    Filters={
        'FullTextSearch': [
            'Linux LAMP Stack',
        ]
    },
    PageSize=20,
    SortBy='Title',
    SortOrder='ASCENDING'
)
for product in linux_instance_search['ProductViewDetails']:
    linux_instance_name = product['ProductViewSummary']['Name']
    if linux_instance_name == 'Linux Instance':
        linux_instance_name = product['ProductViewSummary']['Name']
        linux_instance_id = product['ProductViewSummary']['ProductId']
        print ("Your Linux Instance product name is: " +str(linux_instance_name))
        print ("Your Linux Instance  Product Id is: " +str(linux_instance_id))
        break
if linux_lamp_name != 'Linux Instance':
    print ("Your Linux Instance product was not found")

###############
#Import shared Linux Products into local portfolio from Master Portfolio
###############
linux_pf_id = []
lx_portfolio_id = []
try:
    print("Getting your Portfolio IDs...")
    response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details if x['DisplayName'] == 'Linux Portfolio']
    linux_pf_id = str(ID)[3:-2]
    print("Your Linux Portfolio ID is: " +linux_pf_id)
except:
    print("Error getting Linux Portfolio Id")
    pass
if linux_pf_id != lx_portfolio_id and linux_lamp_id != []:
    try:
        linux_porfolio_list = sc_client.list_portfolios_for_product(
            AcceptLanguage='en',
            ProductId=linux_lamp_id,
            PageSize=20
        )
        linux_portfolio_id = linux_porfolio_list['PortfolioDetails'][0]['Id']
        print ("Your associated Portfolio's for Linux LAMP Stack is " +str(linux_portfolio_id))
    except:
        print ("Your Linux LAMP Stack is not associated with a Portfolio")
        pass
if linux_pf_id != lx_portfolio_id and linux_lamp_id != []:
	try:
	    response = sc_client.associate_product_with_portfolio(
	AcceptLanguage='en',
	ProductId=linux_lamp_id,
	PortfolioId=linux_pf_id,
	SourcePortfolioId=linux_portfolio_id
	)
	except:
		print("Error associating " +linux_lamp_name+ " with portfolio " +linux_portfolio)
		pass

if linux_pf_id != lx_portfolio_id and linux_instance_id != []:
    print "associating instance"
    try:
        response = sc_client.associate_product_with_portfolio(
    AcceptLanguage='en',
    ProductId=linux_instance_id,
    PortfolioId=linux_pf_id,
    SourcePortfolioId=linux_portfolio_id
    )
    except:
        print("Error associating " +linux_instance_name+ " with portfolio " +linux_portfolio)
        pass

###############
#Create a local IAM Role for Portfolio Launch Constraint
###############

try:
    launchconstraintrole_arn = create_roles('SCLaunchConstraint',  scfulluser_arn)
except:
    print("Error creating Launch Contraint Role SCLaunchConstraint")
    pass

    baseline_policy_doc = '{"Version":"2012-10-17","Statement":[{"Sid":"Stmt1503424216000","Effect":"Allow","Action":["ec2:*"],"Resource":["*"]},{"Sid":"Stmt1503424244000","Effect":"Allow","Action":["s3:*"],"Resource":["*"]}]}'
    # baseline_policy_doc = '{ "Version": "2012-10-17", "Statement": [ { "Sid": "Stmt1492787750000", "Effect": "Allow", "Action": [ "acm:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787801000", "Effect": "Allow", "Action": [ "ec2:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787813000", "Effect": "Allow", "Action": [ "codedeploy:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787826000", "Effect": "Allow", "Action": [ "cloudformation:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787839000", "Effect": "Allow", "Action": [ "lambda:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787860000", "Effect": "Allow", "Action": [ "rds:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788192000", "Effect": "Allow", "Action": [ "elasticache:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788214000", "Effect": "Allow", "Action": [ "events:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788227000", "Effect": "Allow", "Action": [ "logs:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788285000", "Effect": "Allow", "Action": [ "cloudwatch:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788317000", "Effect": "Allow", "Action": [ "s3:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788337000", "Effect": "Allow", "Action": [ "sns:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788396000", "Effect": "Allow", "Action": [ "iam:Add*", "iam:Attach*", "iam:Create*", "iam:Get*", "iam:List*", "iam:ListAccountAliases", "iam:ListAttachedGroupPolicies", "iam:PassRole", "iam:Put*", "iam:Upload*", "iam:*", "s3:*", "codedeploy:*", "ec2:*", "lambda:*", "elasticache:*", "application-autoscaling:*", "elasticloadbalancing:*", "sns:*", "cloudfront:*", "cloudwatch:*", "autoscaling:*" ], "Resource": [ "*" ] } ]}'

try:
    baselinepolicy_arn = create_policy_arn('SCBaselinePolicy', baseline_policy_doc , 'Creates the SC policy to be used by the Launch Constraint for the baseline SC product')
except:
    print("Error creating BaseLine Policy SCBaselinePolicy")
    pass

try:
    attach_policy_to_role('SCLaunchConstraint', baselinepolicy_arn)
except:
    print("Error attaching Policy SCBaselinePolicy to Role SCLaunchConstraint")
    pass

try:
	iam_role = iam_client.get_role(
	    RoleName='SCLaunchConstraint'
	)
	role_arn = iam_role['Role']['Arn']
	print(role_arn)
except:
    print("Error getting IAM Role ARN for SCLaunchConstraint")
    pass

###############
#Create Linux Portfolio Launch Constraint
###############
baseline_cs_description = []
instance_cs_description = []
try:
    response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details if x['DisplayName'] == 'Linux Portfolio']
    linux_pf_id = str(ID)[3:-2]
    print("Your Linux Portfolio ID is: " +linux_pf_id)
except:
    print("Error getting Linux Portfolio Id")
    pass
if linux_pf_id != []:
    try:
        baseline_constraint = sc_client.list_baseline_constraint_for_portfolio(
        AcceptLanguage='en',
        PortfolioId=linux_pf_id,
        ProductId=linux_lamp_id,
        PageSize=20
    )
        baseline_cs_description = baseline_constraint['ConstraintDetails'][0]['Description']
    except:
        "Error getting Linux LAMP Stack Constraint description"
        pass
if linux_pf_id != []:
    try:
        instance_constraint = sc_client.list_baseline_constraint_for_portfolio(
        AcceptLanguage='en',
        PortfolioId=linux_pf_id,
        ProductId=linux_instance_id,
        PageSize=20
    )
        instance_cs_description = instance_constraint['ConstraintDetails'][0]['Description']
    except:
        "Error getting Linux Instance Constraint description"
        pass
    if baseline_cs_description != baseline_constraint_description:
        print ("Creating LAMP Stack Lauch Constraint...")
        print linux_lamp_id
        response = sc_client.create_constraint(
            AcceptLanguage='en',
            PortfolioId=linux_pf_id,
            ProductId=linux_lamp_id,
            Parameters='{"RoleArn": "arn:aws:iam::' +account_id+ ':role/SCLaunchConstraint"}',
            Type='LAUNCH',
            Description=baseline_constraint_description,
            IdempotencyToken = token3
        )
    
    if instance_cs_description != instance_constraint_description:
        try:
            print ("Creating Linux Instance Lauch Constraint...")
            response = sc_client.create_constraint(
                AcceptLanguage='en',
                PortfolioId=linux_pf_id,
                ProductId=linux_instance_id,
                Parameters='{"RoleArn": "arn:aws:iam::' +account_id+ ':role/SCLaunchConstraint"}',
                Type='LAUNCH',
                Description=instance_constraint_description,
                IdempotencyToken = token4
            )
            time.sleep(5)
        except:
            print("Error Creating Linux Instance Constraint for " +linux_portfolio)
            pass
        
    
	
###############
#Add tags to local Portfolio
###############
try:
	response = sc_client.update_portfolio(
	    AcceptLanguage='en',
	    Id=linux_pf_id,
	    AddTags=[
	        {
	            'Key': 'SC_Portfolio',
	            'Value': 'Linux Portfolio'
	        }
	    ],
	)
except:
		print("Error adding Tags to Linux Portfolio")
		pass
