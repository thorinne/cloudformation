#!/usr/bin/python
"""
Automate the build of Shared Service Catalog Portfolio, Products and Template baseline_constraint in Child accounts
"""

# AWS All rights reserved - Shared under NDA - Do not distribute without prior authorization.
# This sample, non-production-ready script that creates a Service Catalog Portfolio and the associated products (c) 2017 Amazon Web Services, Inc. or its affiliates. All Rights Reserved. This AWS Content is provided subject to the terms of the AWS Customer Agreement available at http://aws.amazon.com/agreement or other written agreement between Customer and Amazon Web Services, Inc.

# please note that I am not setting the AWS region in this code which means that it will default to the AWS region of my shell where I run this script from.
# you can specify the region in the client call by setting the region_name parameter/value to the appropriate AWS region

###############
#Create Template definitions
###############
import boto3
import random
import time
sc_client = boto3.client('servicecatalog', region_name='us-east-1')
iam_client = boto3.client('iam', region_name='us-east-1')
session_client = boto3.client('sts')
import_portfolios = ['port-rx4vc3kthfxfw']
linux_portfolio_id = 'port-rx4vc3kthfxfw'
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



# IAM functions - remove
# elasticache_policy_arn = 'arn:aws:iam::aws:policy/AmazonElastiCacheFullAccess'
# rds_policy_arn =  'arn:aws:iam::aws:policy/AmazonRDSFullAccess' 
# ec2_policy_arn =  'arn:aws:iam::aws:policy/AmazonEC2FullAccess' 
# vpc_policy_arn =  'arn:aws:iam::aws:policy/AmazonVPCFullAccess' 
# scfulluser_arn = 'arn:aws:iam::aws:policy/ServiceCatalogEndUserFullAccess'
# codedeploy_policy_arn = 'arn:aws:iam::aws:policy/AWSCodeDeployFullAccess'
# cloudwatch_policy_arn = 'arn:aws:iam::aws:policy/CloudWatchFullAccess'
# iam_policy_arn = 'arn:aws:iam::aws:policy/IAMFullAccess'
# lambda_policy_arn = 'arn:aws:iam::aws:policy/AWSLambdaFullAccess'

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

print "################Importing Master Portfolio's, Creating Local Portfolio's and adding Products, Roles and Tags################"

###############
#Import Master Portfolios from import_portfolios list
###############
imported_portfolio_ids = []
try:
    response = sc_client.list_accepted_portfolio_shares(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details]
    imported_portfolio_ids = str(ID)
    print "Your Accepted Portfolio Shares are: " +imported_portfolio_ids
except:
    print "Error getting Portfolio Id"
    pass
difference = [x for x in import_portfolios if x not in imported_portfolio_ids]
print "The Portfolio Shares that are not imported are: " +str(difference)
if difference != []:
	for x in import_portfolios:
		try:
			response = sc_client.accept_portfolio_share(
			    AcceptLanguage='en',
			    PortfolioId=x
			)
			print "Portfolio " +x+ "imported successfully."
		except:
			print "Error importing portfolio " +x
			pass
###############
#Create a local portfolio to add shared Products from Master Portfolio
###############

response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
linux_name = [ x['DisplayName'] for x in response['PortfolioDetails'] ]
print "Your list of Service Catalog Portfolio's are:"
print linux_name
print "\n"
if linux_portfolio not in linux_name:
    try:
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
    except:
        print "Error creating Linux Portfolio " +linux_portfolio
        pass

time.sleep(5)

if linux_portfolio in name:
    print "Your Linux Portfolio " +linux_portfolio+ " already exists"

###############
#Search for Linux products and get ProductId
###############
try:
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
    linux_lamp_name = linux_baseline_search['ProductViewDetails'][0]['ProductViewSummary']['Name']
    linux_lamp_id = linux_baseline_search['ProductViewDetails'][0]['ProductViewSummary']['ProductId']
    print "###############"
    if linux_lamp_name != 'Linux LAMP Stack':
        linux_lamp_name = []
        linux_lamp_id = []

	
    print "Your Linux LAMP Stack Product Id is: " +linux_lamp_id
    print "Your Linux LAMP Stack Product name is: " +linux_lamp_name
except:
    print "Linux LAMP Stack Product Not Found"
    pass

try:
    linux_instance_search = sc_client.search_products_as_admin(
        AcceptLanguage='en',
        PortfolioId=linux_portfolio_id,
        Filters={
            'FullTextSearch': [
                'Linux Instance',
            ]
        },
        PageSize=20,
        SortBy='Title',
        SortOrder='ASCENDING'
    )
    linux_instance_name = linux_instance_search['ProductViewDetails'][0]['ProductViewSummary']['Name']
    linux_instance_id = linux_instance_search['ProductViewDetails'][0]['ProductViewSummary']['ProductId']
    print "###############"
    if linux_instance_name != 'Linux Instance':
        linux_instance_name = []
        linux_instance_id = []

    
    print "Your Linux Instance Product Id is: " +linux_instance_id
    print "Your Linux Instance product name is: " +linux_instance_name
except:
    print "Linux Instance Product Not Found"
    pass

###############
#Import shared Linux Products into local portfolio from Master Portfolio
###############
linux_pf_id = []
lx_portfolio_id = []
try:
    response = sc_client.list_portfolios(AcceptLanguage='en', PageSize=20)
    details = response['PortfolioDetails']
    ID = [x['Id'] for x in details if x['DisplayName'] == 'Linux Portfolio']
    linux_pf_id = str(ID)[3:-2]
    print "Your Linux Portfolio ID is: " +linux_pf_id
except:
    print "Error getting Linux Portfolio Id"
    pass
if linux_pf_id != lx_portfolio_id and linux_lamp_id != []:
    try:
        linux_porfolio_list = sc_client.list_portfolios_for_product(
            AcceptLanguage='en',
            ProductId=linux_lamp_id,
            PageSize=20
        )
        lx_portfolio_id = linux_porfolio_list['PortfolioDetails'][0]['Id']
        print "Your associated Portfolio's for Linux LAMP Stack is " +str(lx_portfolio_id)
    except:
        print "Error getting the Portfolio Id for product " +str(linux_lamp_name)
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
		print "Error associating " +linux_lamp_name+ " with portfolio " +linux_portfolio
		pass

if linux_pf_id != lx_portfolio_id and linux_instance_id != []:
    try:
        response = sc_client.associate_product_with_portfolio(
    AcceptLanguage='en',
    ProductId=linux_instance_id,
    PortfolioId=linux_pf_id,
    SourcePortfolioId=linux_portfolio_id
    )
    except:
        print "Error associating " +linux_instance_name+ " with portfolio " +linux_portfolio
        pass

###############
#Create a local IAM Role for Portfolio Launch Constraint
###############

try:
    launchconstraintrole_arn = create_roles('SCLaunchConstraint',  scfulluser_arn)
except:
    print "Error creating Launch Contraint Role SCLaunchConstraint"
    pass

try:
    baseline_policy_doc = '{"Version":"2012-10-17","Statement":[{"Sid":"Stmt1503424216000","Effect":"Allow","Action":["ec2:*"],"Resource":["*"]},{"Sid":"Stmt1503424244000","Effect":"Allow","Action":["s3:*"],"Resource":["*"]}]}'
    # baseline_policy_doc = '{ "Version": "2012-10-17", "Statement": [ { "Sid": "Stmt1492787750000", "Effect": "Allow", "Action": [ "acm:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787801000", "Effect": "Allow", "Action": [ "ec2:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787813000", "Effect": "Allow", "Action": [ "codedeploy:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787826000", "Effect": "Allow", "Action": [ "cloudformation:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787839000", "Effect": "Allow", "Action": [ "lambda:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492787860000", "Effect": "Allow", "Action": [ "rds:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788192000", "Effect": "Allow", "Action": [ "elasticache:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788214000", "Effect": "Allow", "Action": [ "events:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788227000", "Effect": "Allow", "Action": [ "logs:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788285000", "Effect": "Allow", "Action": [ "cloudwatch:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788317000", "Effect": "Allow", "Action": [ "s3:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788337000", "Effect": "Allow", "Action": [ "sns:*" ], "Resource": [ "*" ] }, { "Sid": "Stmt1492788396000", "Effect": "Allow", "Action": [ "iam:Add*", "iam:Attach*", "iam:Create*", "iam:Get*", "iam:List*", "iam:ListAccountAliases", "iam:ListAttachedGroupPolicies", "iam:PassRole", "iam:Put*", "iam:Upload*", "iam:*", "s3:*", "codedeploy:*", "ec2:*", "lambda:*", "elasticache:*", "application-autoscaling:*", "elasticloadbalancing:*", "sns:*", "cloudfront:*", "cloudwatch:*", "autoscaling:*" ], "Resource": [ "*" ] } ]}'
except:
    print "Error creating BaseLine Policy Doc"
    pass

try:
    baselinepolicy_arn = create_policy_arn('SCBaselinePolicy', baseline_policy_doc , 'Creates the SC policy to be used by the Launch Constraint for the baseline SC product')
except:
    print "Error creating BaseLine Policy SCBaselinePolicy"
    pass

try:
    attach_policy_to_role('SCLaunchConstraint', baselinepolicy_arn)
except:
    print "Error attaching Policy SCBaselinePolicy to Role SCLaunchConstraint"
    pass

try:
	iam_role = iam_client.get_role(
	    RoleName='SCLaunchConstraint'
	)
	role_arn = iam_role['Role']['Arn']
	print role_arn
except:
    print "Error getting IAM Role ARN for SCLaunchConstraint"
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
    print "Your Linux Portfolio ID is: " +linux_pf_id
except:
    print "Error getting Linux Portfolio Id"
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
        try:
            response = sc_client.create_constraint(
                AcceptLanguage='en',
                PortfolioId=linux_pf_id,
                ProductId=linux_lamp_id,
                Parameters='{"RoleArn": "arn:aws:iam::' +account_id+ ':role/SCLaunchConstraint"}',
                Type='LAUNCH',
                Description=baseline_constraint_description,
                IdempotencyToken = token3
            )
        except:
            print "Error Creating Linux LAMP Stack Constraint for " +linux_portfolio
            pass

    if instance_cs_description != instance_constraint_description:
        try:
            response = sc_client.create_constraint(
                AcceptLanguage='en',
                PortfolioId=linux_pf_id,
                ProductId=linux_instance_id,
                Parameters='{"RoleArn": "arn:aws:iam::' +account_id+ ':role/SCLaunchConstraint"}',
                Type='LAUNCH',
                Description=instance_constraint_description,
                IdempotencyToken = token4
            )
        except:
            print "Error Creating Linux Instance Constraint for " +linux_portfolio
            pass
        
    time.sleep(5)
	
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
		print "Error adding Tags to Linux Portfolio"
		pass
