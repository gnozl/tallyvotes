import csv

class Ballot:
    def __init__(self, ID, votes, alive = True):  

	    self.ID = ID
	    self.votes = votes
	    self.first = votes[0]
	    self.second = votes[1]
	    self.third = votes[2]
	    self.alive = alive


def import_csv():
	ballot = {}

	with open('064clean.csv', newline='') as csvfile:
		ballotReader = csv.DictReader(csvfile)

		for i in ballotReader:
			if i['VoterID'] in dq_list: continue
			voterID = i['VoterID']
			votes = [i['1st Place'], i['2nd Place'], i['3rd Place'] ]
			ballot[voterID] = Ballot(voterID, votes)

	return ballot


def disqualified():
	dq_list = []

	with open("dq.txt") as file:
		dq_list = file.read().splitlines()

	return dq_list


def score_voting(first, second, third):
	tally = {}
	for ID in ballot:

		for index, vote in ballot[ID].votes:
			print(index)
			if vote not in tally:
				tally[vote] = 0
			tally[vote] += 3-index

"""		if ballot[ID].first not in tally:
			tally[ballot[ID].first] = 0
		if ballot[ID].second not in tally:
			tally[ballot[ID].second]= 0
		if ballot[ID].third not in tally:
			tally[ballot[ID].third] = 0
"""
		tally[ballot[ID].first]	+= first
		tally[ballot[ID].second]+= second
		tally[ballot[ID].third]	+= third

		for dq in dq_list:
			if dq in tally:
				del tally[dq]

	winner = max(tally, key=tally.get)
	print("Winner is " + winner)

	return tally


def instant_runoff():
	runoff = copy.deepcopy(ballot)
	candidates = []
	for vote in runoff
		if runoff[vote].first not in candidates:
			candidates.append(runoff[vote].first)
		if runoff[vote].second not in candidates:
			candidates.append(runoff[vote].second)
		if runoff[vote].third not in candidates:
			candidates.append(runoff[vote].third)


def tally_votes(mode):

	if mode == "1":
		mode = "Point"
		tally = score_voting(3,2,1)	

	elif mode == "2": 
		mode = "Approval"
		tally = score_voting(1,1,1)

	elif mode == "3": 
		mode = "Plurality"
		tally = score_voting(1,0,0)

	elif mode == "4":
		mode = "Instant Runoff"
		tally = instant_runoff()

	else: return Exception("tally_votes argument error")


def run():
	print("Enter tallying method: ")
	print("1. Approval\n2. Point Value\n3. First Past the Post\n4. Instant Runoff")
	mode = input()
	options = ["1", "2", "3","4"]
	if mode not in options:
		return print("Please select an available option.")
	tally_votes(mode)


dq_list = disqualified()
ballot = import_csv()
run()

while(input("Run again? (Y/N): ") in ['y', 'Y', 'yes', 'Yes', 'YES']):
	run()

