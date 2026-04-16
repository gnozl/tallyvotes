from argparse import ArgumentParser

class Ballot:
    def __init__(self, ID, votes, dead = False):  

	    self.ID = ID
	    self.votes = votes
	    self.dead = dead


def import_csv(filename="votes.csv"):
	import csv

	ballots = {}

	if args.filename:
		filename = args.filename

	with open(filename, newline='') as csvfile:
		ballotReader = csv.DictReader(csvfile)

		for i in ballotReader:
			if i['VoterID'] in dq_list: 
				continue
				
			voterID = i.pop('VoterID')

			keys = i.keys()
			votes = [i[key] for key in keys if i[key]]

			ballots[voterID] = Ballot(voterID, votes)

	return ballots


def disqualified(filename="dq.txt"):

	dq_list = []

	#if (input("Import DQ list? ") not in ['y', 'Y', 'yes', 'Yes', 'YES']):
	#	return dq_list

	if not args.dqlist:
		return dq_list

	filename = args.dqlist

	with open(filename) as file:
		dq_list = file.read().splitlines()

	for dq in dq_list:
		print(f"{dq} has been disqualified.")

	return dq_list


def get_candidates():
	candidates = []
	for voterID in ballot:
		for vote in ballot[voterID].votes:
			if vote == "":
				continue
			if vote not in candidates:
				candidates.append(vote)

	return candidates


def score_voting(points="default"):
	if points == "default":
		points = len(candidates)

	tally = {}

	for ID in ballot:

		if ballot[ID].dead:
			continue

		for index, vote in enumerate(ballot[ID].votes):
			if vote in dq_list:
				continue
			if vote not in tally:
				tally[vote] = 0
			if type(points) == list:
				if 0 <= index < len(points):
					tally[vote] += points[index]
			elif type(points) == int:
				if 0 <= index < points:
					tally[vote] += points - index

	if args.verbose: print(tally)

	return tally


def instant_runoff():
	import copy
	ir_ballot = copy.deepcopy(ballot)			# dict of Ballot 
	live_candidates = copy.deepcopy(candidates) # list of string

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
					if args.verbose: print("Round " + str(runoff_round) + " - Eliminated: " + candidate)
			loser = min(runoff_total, key=runoff_total.get)
			live_candidates.remove(loser)
			if args.verbose: print("Round " + str(runoff_round) + " - Eliminated: " + loser)

	if args.verbose:
		for candidate in live_candidates:
			if candidate != winner:
				print("Round " + str(runoff_round) + " - Eliminated: " + candidate)

	return winner


def tally_votes(mode):

	if mode == "1" or mode == "0":
		tally = score_voting()
		winner = max(tally, key=tally.get)
		print(f"\033[32mPoint Value Winner is {winner} with {tally[winner]} out of {len(candidates)*voters} maximum possible points.\033[0m\n")

	if mode == "2" or mode == "0": 
		tally = score_voting([1 for x in candidates])
		winner = max(tally, key=tally.get)
		print(f"\033[32m{tally[winner]} out of {voters} voters approve of {winner} as the winner.\033[0m\n")

	if mode == "3" or mode == "0": 
		tally = score_voting([1])
		winner = max(tally, key=tally.get)
		percent = 100 * tally[winner] / voters
		print(f"\033[32m{winner} won a plurality, with {tally[winner]} first place votes ({percent:.2f}%).\033[0m\n")

	if mode == "4" or mode == "0":
		winner = instant_runoff()
		print(f"\033[32m{winner} received a majority of the vote in the Instant Runoff.\033[0m\n")

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

parser = ArgumentParser()
parser.add_argument("filename", type=str, help="path to CSV with vote data to be read.")
parser.add_argument("-d", "--disqualified", dest="dqlist", help="TXT with names of disqualified voters/poems.")
parser.add_argument("-v", "--verbose", action='store_true', help='Enable verbose mode')
args = parser.parse_args()

dq_list = disqualified()
ballot = import_csv()
candidates = get_candidates()
voters = len(ballot)
run()
# while(input("Run again? (Y/N): ") in ['y', 'Y', 'yes', 'Yes', 'YES']):
#	run()
