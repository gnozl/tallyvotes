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
		print(f"{dq} has been disqualified.")

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
	ir_ballot = copy.deepcopy(ballot)
	live_candidates = copy.deepcopy(candidates)

	for candidate in live_candidates:
		if candidate in dq_list:
			live_candidates.remove(candidate)
			continue
		
	winner = False
	runoff_round = 0
	while not winner:

		# RESET TOTALS
		runoff_total = {}
		votes_cast = 0
		runoff_round += 1

		for candidate in live_candidates:
			runoff_total[candidate] = 0 

		# COUNT BALLOTS
		for ID in ir_ballot:
			if ir_ballot[ID].dead:
				continue

			vote_exhausted = True

			for vote in ir_ballot[ID].votes:
				if vote in live_candidates:
					vote_exhausted = False
					runoff_total[vote] += 1
					votes_cast += 1
					break
			
			if vote_exhausted:
				ir_ballot[ID].dead = True



		# CHECK FOR WINNER
		votes_needed = 1 + votes_cast // 2 
		# print("Round " + str(runoff_round))
		# print("Votes needed: " + str(votes_needed))
		# print("Live Ballots: " + str(votes_cast))
		# print(runoff_total)

		for poem in runoff_total:
			if runoff_total[poem] >= votes_needed:
				winner = poem

		# REMOVE LOWEST PERFORMING CANDIDATES
		if winner == False:
			for candidate in live_candidates:
				if runoff_total[candidate] == 0:
					live_candidates.remove(candidate)
					del runoff_total[candidate]
					# print(candidate + " out in round " + str(runoff_round))
			loser = min(runoff_total, key=runoff_total.get)
			live_candidates.remove(loser)
			# print(loser + " out in round " + str(runoff_round))

	return winner



def tally_votes(mode):

	if mode == "1" or mode == "0":
		tally = score_voting([3,2,1])
		winner = max(tally, key=tally.get)
		print(f"Point Value Winner is {winner} with {tally[winner]} out of {3*voters} maximum possible points.")

	if mode == "2" or mode == "0": 
		tally = score_voting([1,1,1])
		winner = max(tally, key=tally.get)
		print(f"{tally[winner]} out of {voters} voters approve of {winner} as the winner.")

	if mode == "3" or mode == "0": 
		tally = score_voting([1])
		winner = max(tally, key=tally.get)
		percent = 100 * tally[winner] / voters
		print(f"{winner} won a plurality, with {tally[winner]} first place votes ({percent:.2f}%).")

	if mode == "4" or mode == "0":
		winner = instant_runoff()
		print(f"{winner} received a majority of the vote in the Instant Runoff.")

	#TODO: MINMAX Winning Votes
	#TODO: MINMAX Margins
	#TODO: MINMAX Pairwise Opposition

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

