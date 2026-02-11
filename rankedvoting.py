class Ballot:
    def __init__(self, ID, votes, dead = False):  

	    self.ID = ID
	    self.votes = votes
	    self.dead = dead


def import_csv(filename="votes.csv"):
	import csv

	ballots = {}

	with open(filename, newline='') as csvfile:
		ballotReader = csv.DictReader(csvfile)

		for i in ballotReader:
			if i['VoterID'] in dq_list: 
				continue
			voterID = i['VoterID']
			votes = [i['1st Place'], i['2nd Place'], i['3rd Place'] ]
			#TODO: Allow every candidate to be ranked, not just top 3 
			ballots[voterID] = Ballot(voterID, votes)

	return ballots


def disqualified(filename="dq.txt"):

	dq_list = []

	if (input("Import DQ list? ") not in ['y', 'Y', 'yes', 'Yes', 'YES']):
		return dq_list

	with open(filename) as file:
		dq_list = file.read().splitlines()

	for dq in dq_list:
		print(dq + " has been disqualified.")

	return dq_list


def get_candidates():
	candidates = []
	for voterID in ballot:
		for vote in ballot[voterID].votes:
			if vote not in candidates:
				candidates.append(vote)

	return candidates


def score_voting(points):

	tally = {}

	for ID in ballot:

		if ballot[ID].dead:
			continue

		for index, vote in enumerate(ballot[ID].votes):
			if vote in dq_list:
				continue
			if vote not in tally:
				tally[vote] = 0
			if 0 <= index < len(points):
				tally[vote] += points[index]



	return tally


def instant_runoff():
	import copy
	new_ballot = copy.deepcopy(ballot)
	new_candidates = copy.deepcopy(candidates)

	#TODO: Finish this


def tally_votes(mode):

	if mode == "1" or "0":
		mode = "Point"
		tally = score_voting([3,2,1])
		winner = max(tally, key=tally.get)
		print("Point Value Winner is " + winner + " with " + str(tally[winner]) + " out of " + str(3*voters) + " maximum possible points.")


	if mode == "2" or "0": 
		mode = "Approval"
		tally = score_voting([1,1,1])
		winner = max(tally, key=tally.get)
		print(str(tally[winner]) + " out of " + str(voters) + " voters approve of " + winner + " as the winner.")


	if mode == "3" or "0": 
		mode = "Plurality"
		tally = score_voting([1])
		winner = max(tally, key=tally.get)
		print(winner + " won, with " + str(tally[winner]) + " first place votes.")


	elif mode == "4" or "0":
		mode = "Instant Runoff"
		tally = instant_runoff()

	#TODO: 

	else: return Exception("tally_votes argument error")


def run():
	print("Enter tallying method: ")
	print("1. Point Value\n2. Approval\n3. First Past the Post\n4. Instant Runoff\n0. Run all the simulations.")
	mode = input()
	options = ["0", "1", "2", "3","4"]
	if mode not in options:
		return print("Please select an available option.")
	tally_votes(mode)


dq_list = disqualified()
ballot = import_csv()
candidates = get_candidates()
voters = len(ballot)
run()

while(input("Run again? (Y/N): ") in ['y', 'Y', 'yes', 'Yes', 'YES']):
	run()

