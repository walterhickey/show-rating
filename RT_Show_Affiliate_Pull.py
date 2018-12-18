from tqdm import tqdm
import requests
import sys
try:
	show1 = sys.argv[1].strip()
except:
	show1 = raw_input("Enter the Rotten Tomatoes URL slug of the show you want: ")
out = ""
#show = "riverdale"
#show = "sense8"

star4 = '<span class="glyphicon glyphicon-star"></span><span class="glyphicon glyphicon-star"></span><span class="glyphicon glyphicon-star"></span><span class="glyphicon glyphicon-star">'
sct = 0 #season count
s = [] #season urls
l = [] #positive reviewer urls
o = [] #all mentioned shows
ot = [] #temporaty show list per reviewers
ou = [] #all unique shows mentioned



#find out how many seasons
r = requests.get("https://www.rottentomatoes.com/tv/" + show1 + "/")
seasons = r.text
seasons = seasons[seasons.find('<section id="seasonList"'):]
seasons = seasons[:seasons.find('</section>')]
seasonct = seasons.count('<a href="/tv/')
while sct < seasonct:
	sct = sct + 1
	seasons = seasons[seasons.find('<a href="/tv/')+9:]
	s.append(seasons[:seasons.find('"')])
	
	
#run through list of season slugs
for season in s:
	k = 1
	#find how many pages of reviews each season has
	url = "https://www.rottentomatoes.com" + season + "/reviews/?page=" + str(k) + "&type=user&sort="
	r = requests.get("https://www.rottentomatoes.com" + season + "/reviews/?page=" + str(k) + "&type=user&sort=")
	pages = r.text
	#print url
	pages = pages[pages.find('<span class="pageInfo">Page 1 of ')+33:]
	pages = pages[:pages.find("</span>")]
	#save integer of number of pages in max_pages
	try:
		max_pages = int(float(pages))
	except:
		max_pages = 0
	print season + " - pages:" + str(max_pages)
	#cycle through all reviews within the season
	for k in tqdm(range(max_pages)):
		url = "https://www.rottentomatoes.com" + season + "/reviews/?page=" + str(k) + "&type=user&sort="
		r = requests.get(url)
		page = r.text
		page = page[page.find('<span class="pageInfo">Page')+27:]
		page = page[:page.find('<span class="pageInfo">Page')]
		#look out for these strings:
		rev_ct = page.count('<a class="bold unstyled articleLink" href="/user/')
		while rev_ct > 0:
			rev_ct = rev_ct - 1
			#find user pages
			page = page[page.find('<a class="bold unstyled articleLink" href="/user/')+43:]
			slug = page[:page.find('</div> </div>')]
			chonk = page[:page.find('<a class="')]
			slug = slug[:slug.find('/">')+1]
			user = "https://www.rottentomatoes.com" + slug + "tvratings"
			if star4 in chonk:
				if user in l:
					continue
				else:	
					l.append(user)
print "Completed scrape, found 4+ star reviews from " + str(len(l))	+ " users"


#user scrape!
morethan = 0
only = 0
nil = 0
for u in tqdm(l):
	page = requests.get(u).text
	rev_ct = page.count('<div class="bottom_divider media">')

	#FIND ALL SHOWS
	while rev_ct > 0:
		page = page[page.find('class="bold" data-pageheader="" href="/tv/')+42:]
		chonk = page[:page.find('<div class="bottom_divider')]
		show = chonk[:chonk.find('/')]
		#If the shows is 4 star or better, add it to ot, the temp list
		if star4 in chonk:
			if show in ot:
				continue	
			else:	
				ot.append(show)
		rev_ct = rev_ct - 1
	
	#what kind of user was this?
	if len(ot) > 1:
		morethan = morethan + 1
	elif len(ot) == 1:
		only = only + 1
	else:
		nil = nil + 1
		
	#bag em and tag em
	f = len(ot)
	kk= 0					
	while kk < f:
		kk = kk + 1
		b = ot.pop()
		#is it the first time we've seen this show?
		if b in ou:
			#add it to the list of all shows
			o.append(b)
		else:
			#add it to the list of all shows
			o.append(b)
			#unique shows
			ou.append(b)

			
#HE CONTORTS
print "REPORT: " + str(nil) + " dead pages. Of " + str(only+morethan) + " reviews, " + str(morethan) + " named an additional show. Top 100:"

#HE SORTS
final = []
for q in ou:
	tmp = (q,o.count(q))
	final.append(tmp)	
final.sort(key=lambda tup: tup[1],reverse=True )

token = 5
#HE REPORTS
for i in final:
	if i[1]>=5:
		print i[0] + ", " + str(i[1]) + " viewers also loved, " + str(int(100.0*i[1]/(only + morethan))) + "% of reviewers."