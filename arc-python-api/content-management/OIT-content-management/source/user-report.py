hub = GIS(

  url="https://colorado-gis.maps.arcgis.com/",

  username=os.getenv('HUB_USER_NAME'),

  password=os.getenv('PASSWORD')

)




users = []

for i in hub.users.search(query = '*', max_users = 10000):

  last_login_formatted = datetime(*time.localtime(i.lastLogin/1000)[:6], tzinfo=timezone.utc)

  now = datetime.now()

  if (int(last_login_formatted.strftime("%y"))-int(now.strftime("%y")))!=0:

    if (int(last_login_formatted.strftime("%m"))-int(now.strftime("%m")))==0:

      try:

        gis.users.delete_users(i)

      except:

        print("can't delete user")

  users.append([i.fullName, i.username, last_login_formatted, str(i.groups), i.role, i.email, i.availableCredits,i.assignedCredits])

users = pd.DataFrame(users, columns=['Full Name', 'Username','Last Login','Groups','Role','Email','Available Credits','Assigned Credits'])