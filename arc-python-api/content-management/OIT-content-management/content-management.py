from email.message import EmailMessage
import smtplib
from arcgis.gis import GIS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ssl
import pandas as pd
# from dotenv import load_dotenv
import os

# load_dotenv()

# folder to save content csvs to
folder = r"C:\Users\is_olson\Documents\Projects\SSO_Update\python-folder"

# To run this script you must have anaconda installed https://www.anaconda.com/download
# You must edit this file and the .bat file in order to run it correctly


# accessing AGOL
################################# Add your ArcGIS Online URL, username and password. You must have admin privileges. ############################################
# gis = GIS(
#     url="ARCGIS ONLINE ORGANIZATION URL",
#     username=os.getenv('USER_NAME'),
#     password=os.getenv('PASSWORD')
# )

# gis = GIS(url="https://c3.maps.arcgis.com", username="aolson_c3", password="xxxx", profile="aolson_prfl2")
gis = GIS(url="https://c3.maps.arcgis.com", profile="aolson_prfl")

# list of all users in my organization
user_list = gis.users.search(query='*', max_users=10000)
total_content_count = 0
for i in user_list:
    total_content_count += gis.content.advanced_search(query="owner: " + i.username, max_items=-1, return_count=True)

print(total_content_count)

# # getting items and their details for all members i want to email
# for i in user_list:
#     #################################
#     # Enter the AGOL usernames of the people you want to include. Add more if necessary.
#     # If you are sending to everyone in your organization, there is a way to programmatically get it using
#     # gis.users.search(query = '*', max_users = 10000)
#     # ############################################
#     if i.username == "aolson_c3_Test" or i.username == "aolson_c3_Test_2" or i.username == "aolson_c3":
#
#         # get the content from the member
#         member_content_count = gis.content.advanced_search(query="owner: " + str(i.username), max_items=-1,
#                                                            return_count=True)
#         member_content = gis.content.advanced_search(query="owner: " + i.username, max_items=-1, as_dict=True)
#         member_content_df = pd.DataFrame(member_content['results'])
#         member_content_df = member_content_df[
#             ["id", "owner", "title", "type", "description", "tags", "categories", "url", "access", "ownerFolder",
#              "protected", "numViews"]]
#
#         # sending the df to a csv and saving it locally to send
#         member_content_df.to_csv(folder + "\\" + str((i.username).split('.')[0].lower()) + "Content.csv")
#         # items not protected
#         protected = str(sum(member_content_df.value_counts(["access", "protected"]).reset_index().query(
#             "access=='public' and protected==False")[0].tolist()))
#         # missing public description
#         description_public = str(sum(
#             member_content_df.value_counts(['access', 'description'], dropna=False).reset_index().query(
#                 "access=='public' and description==''")[0].tolist()))
#         # missing all descriptions
#         description = str(sum(
#             member_content_df.value_counts(['access', 'description'], dropna=False).reset_index().query(
#                 "description==''")[0].tolist()))
#         # items not in a folder
#         owner_folder = str(sum(
#             member_content_df.value_counts(["ownerFolder"], dropna=False).reset_index().query("ownerFolder==''")[
#                 0].tolist()))
#         # items without a category
#         categories = str(
#             member_content_df["categories"].explode().value_counts(dropna=False).reset_index().fillna('None').set_index(
#                 'index').to_dict()['categories']['None'])
#         # items without tags
#         # have to run try statement for tags since there is an error if there are no items
#         try:
#             tags_table = \
#             member_content_df["tags"].explode().value_counts(dropna=False).reset_index().fillna('None').set_index(
#                 'index').to_dict()['tags']
#             no_tags = tags_table['None']
#             empty_tags = tags_table['']
#             tags = str(no_tags + empty_tags)
#         except:
#             tags = "0"

        # #################################
        # # Enter sender email and all other receiver emails, corrosponding usernames, and names. Add more if neccessary.
        # # ############################################
        # # defining users i want to send to
        # sender = "EMAIL"
        # password = os.getenv('SENDER_PASSWORD')
        #
        # if i.username == "USERNAME":
        #     receiver = "EMAIL"
        #     name = "NAME"
        # elif i.username == "USERNAME":
        #     receiver = "EMAIL"
        #     name = "NAME"
        # elif i.username == "USERNAME":
        #     receiver = "EMAIL"
        #     name = "NAME"
        # elif i.username == "USERNAME":
        #     receiver = "EMAIL"
        #     name = "NAME"
        # else:
        #     receiver = sender
        #     name = "NAME"
        #
        # # setting up email content
        # ################################# Change words in email to fit your organizations standards. ############################################
        # subject = "ArcGIS Online Quarterly Content Review"
        # body = """\
        # <html>
        # <head></head>
        # <body>
        # """ + name + """,
        # <br><br>
        # You have """ + str(member_content_count) + """ items in your ArcGIS Online account. This takes up """ + str(
        #     round(member_content_count / total_content_count * 100, 1)) + """% of the organization's content. Attached is the list of your ArcGIS Online items, please ensure your content follows the <a href="https://docs.google.com/document/d/17bbR2V42jz6CDmxsWTgYMYSdWit5OK_9xDvkNMGvTrw/edit?usp=sharing">SOP</a>.
        # <br><br>
        # <b>Names: </b>Items must be named with an understandable name, formatted with spaces (for example "Cool map" instead of "Cool_map"). If they are DEV apps or maps, please add DEV at the end.
        # <br><br>
        # <b>Descriptions: </b>Please ensure all of your items have a description. At the very least, all public items must have a description. You have """ + description_public + """ public items without a description and """ + description + """ items total without a description.
        # <br><br>
        # <b>Tags: </b>Content must have the proper tags with the proper naming conventions. Please make sure tags are formatted with spaces (for example: "Colorado Counties" instead of "Colorado_Counties"). Dev web maps must have the tag "Web Map Development" and dev web apps must have the tag "Web App Development". Prod web maps must have the tag "Web Map Production" prod web apps must have the tag "Web App Production". You have """ + tags + """ items without tags. Please make sure tags are useful (do not include tags like "test").
        # <br><br>
        # <b>Folders: </b>Putting your content into folders will help with your personal organization. """ + owner_folder + """ of your items are not in a folder.
        # <br><br>
        # <b>Categories: </b>All public items must have a category. Please contact an administrator if you need a category created. You have """ + categories + """ public items not in a category.
        # <br><br>
        # <b>Sharing: </b>Content shared with the public must be delete-protected. """ + protected + """ of your public items are unprotected. Use groups to share content with the correct people or teams within the organization, and refrain from sharing to the organization.
        # <br><br>
        # <b>Status: </b>This should be enabled for all production and development items. It is encouraged on all important items. When marking authority it will also enable delete protection. All archived items should be deprecated. If you need an item to be marked authoritative, let an administrator know.
        # <br><br>
        # <b>Deleting an item: </b>If your item is public, mark the item private and deprecated and wait a month before deleting the item.
        # <br><br>
        # <b>Terms of use: </b>All content should have the following information in the terms of use section-
        # <br>“The data made available here has been modified for use from its original source, which is the State of Colorado. THE STATE OF COLORADO MAKES NO REPRESENTATIONS OR WARRANTY AS TO THE COMPLETENESS, ACCURACY, TIMELINESS, OR CONTENT OF ANY DATA MADE AVAILABLE THROUGH THIS SITE. THE STATE OF COLORADO EXPRESSLY DISCLAIMS ALL WARRANTIES, WHETHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE. The data is subject to change as modifications and updates are complete. It is understood that the information contained in the Web feed is being used at one's own risk.”
        # </body>
        # </html>
        #     """

        # # sending email
        # body.encode()
        # # sending email
        # em = MIMEMultipart()
        # em["From"] = sender
        # em["To"] = receiver
        # em["Subject"] = subject
        # em.attach(MIMEText(body, 'html'))
        # filename = (folder + name + "Content.csv")
        # # attach csv of content
        # attachment = open(filename, "rb")
        # p = MIMEBase('application', 'octet-stream')
        # p.set_payload((attachment).read())
        # encoders.encode_base64(p)
        # p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        # em.attach(p)
        # text = em.as_string()
        # context = ssl.create_default_context()
        # s = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
        # s.login(sender, password)
        # s.sendmail(sender, receiver, text)
        # s.quit()