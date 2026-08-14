from argparse import ArgumentParser
import pprint
from dataclasses import dataclass

class Ballot:
    def __init__(self, ID: str, votes: dict, dead: bool = False):  

	    self.ID 	: str 	= ID
	    self.votes 	: dict 	= votes
	    self.dead 	: bool 	= dead

def import_csv(filename: str):
	import csv

	ballots = {}

	if filename[-4:] != ".csv":
		raise Exception("Votes must be in CSV format.\n")

	with open(filename, newline='') as csvfile:
		ballotReader = csv.DictReader(csvfile)


		while True:
			primary_key = input("Please enter the primary key: ")

			if primary_key == "":
				if "VoterID" in ballotReader.fieldnames:
					primary_key = "VoterID"
					break
				else: 
					pass
			
			elif primary_key not in ballotReader.fieldnames:
				print("Key not found in CSV.\n")

			else:
				break

		
		remove_keys = []
		while True:
			i = input("Keys to remove: ")
			if i == "" or i  == "None":
				remove_keys.append("TimeStamp")
				remove_keys.append("Competitor?")
				break

			else: remove_keys.append(i)


		for ballot in ballotReader:

			if ballot[primary_key] in DQLIST:
				print(ballot[primary_key] + " was disqualified.\n") 
				continue

			# for key in remove_keys:
			# 	if key in ballot.keys():
			# 		ballot.pop(key)

			[ballot.pop(key) for key in remove_keys if key in ballot.keys()]
				
			voterID = ballot.pop(primary_key)
			keys = ballot.keys()
			votes = [ballot[key] for key in keys if ballot[key]]

			ballots[voterID] = Ballot(voterID, votes)

	return ballots

def disqualified(filename):

	dq_list = []

	#if (input("Import DQ list? ") not in ['y', 'Y', 'yes', 'Yes', 'YES']):
	#	return dq_list

	if not filename:
		return dq_list

	if filename[-4:] != ".txt":
		raise Exception("DQ file must be in TXT format.")

	with open(filename) as file:
		dq_list = file.read().splitlines()

	for dq in dq_list:
		print(f"{dq} has been disqualified.")

	return dq_list

def get_candidates():
	candidates = []
	for voterID in BALLOTS:
		for vote in BALLOTS[voterID].votes:
			if vote == "":
				continue
			if vote not in candidates:
				candidates.append(vote)

	return candidates

def score_voting(mode, points):

	tally = {}

	for ID in BALLOTS:

		if BALLOTS[ID].dead:
			continue

		for index, vote in enumerate(BALLOTS[ID].votes):
			if vote in DQLIST:
				continue
			if vote not in tally:
				tally[vote] = 0
			if type(points) == list:
				if 0 <= index < len(points):
					tally[vote] += points[index]
			elif type(points) == int:
				if 0 <= index < points:
					tally[vote] += points - index

	tally = dict(sorted(tally.items(), key=lambda item: item[1]))

	if ARGS.verbose: pprint.pp(tally)

	winner = max(tally, key=tally.get)

	match mode:
		case "PV10":
			print(f"\033[32mTop Ten Winner is {winner} with {tally[winner]} out of {10*VOTERS} maximum possible points.\033[0m\n")
		case "PMAX":
			print(f"\033[32mPoint Value Winner is {winner} with {tally[winner]} out of {len(CANDIDATES)*VOTERS} maximum possible points.\033[0m\n")
		case "APPR":
			print(f"\033[32m{tally[winner]} out of {VOTERS} voters approve of {winner} as the winner.\033[0m\n")
		case "FPTP":
			percent = 100 * tally[winner] / VOTERS
			print(f"\033[32m{winner} won a plurality, with {tally[winner]} first place votes ({percent:.2f}%).\033[0m\n")

def instant_runoff():
	import copy
	ir_ballot = copy.deepcopy(BALLOTS)			# dict of Ballot 
	live_candidates = copy.deepcopy(CANDIDATES) # list of string

	for candidate in live_candidates:
		if candidate in DQLIST:
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

		for candidate in runoff_total:
			if runoff_total[candidate] >= votes_needed:
				winner = candidate

		# REMOVE LOWEST PERFORMING CANDIDATES
		if winner == False:
			for candidate in live_candidates:
				if runoff_total[candidate] == 0:
					live_candidates.remove(candidate)
					del runoff_total[candidate]
					if ARGS.verbose: print("Round " + str(runoff_round) + " - Eliminated: " + candidate)
			loser = min(runoff_total, key=runoff_total.get)
			live_candidates.remove(loser)
			if ARGS.verbose: print("Round " + str(runoff_round) + " - Eliminated: " + loser)

	if ARGS.verbose:
		for candidate in live_candidates:
			if candidate != winner:
				print("Round " + str(runoff_round) + " - Eliminated: " + candidate)

	print(f"\033[32m{winner} received a majority of the vote in the Instant Runoff.\033[0m\n")

def tally_votes(mode):

	METHOD = {
		"PMAX" : "score_voting('PMAX', len(CANDIDATES))",
		"PV10" : "score_voting('PV10', 10)",
		"APPR" : "score_voting('APPR', [1 for x in CANDIDATES])",
		"FPTP" : "score_voting('FPTP', [1])",
		"INST" : "instant_runoff()"
		}

	if mode == "ALL":
		for x in METHOD:
			eval(METHOD[x])
		return

	eval(METHOD[mode])

	#TODO: MINMAX Winning Votes
	#TODO: MINMAX Margins
	#TODO: MINMAX Pairwise Opposition

	# return Exception("tally_votes argument error")

def parse_args():
	parser = ArgumentParser()
	parser.add_argument("votes", type=str, help="path to CSV with vote data to be read.")
	parser.add_argument("-dq", "--disqualify", dest="dqlist", help="path to TXT with names of disqualified voters/votes.")
	parser.add_argument("-v", "--verbose", action='store_true', help='Enable verbose mode')
	parser.add_argument("-a", "--all", action='store_true', help='Run all tallies')
	#TODO: Add create votes / simulation mode

	return parser.parse_args()

def run():

	global ARGS, DQLIST, BALLOTS, CANDIDATES, VOTERS

	ARGS = parse_args()
	DQLIST = disqualified(ARGS.dqlist)
	BALLOTS = import_csv(ARGS.votes)
	CANDIDATES = get_candidates()
	VOTERS = len(BALLOTS)

	if ARGS.all:
		tally_votes("ALL")
		return

	OPTION = {
		"PMAX" : "Point Value w/ unlimited votes per ballot",
		"PV10" : "Point Value w/ up to 10 votes per ballot",
		"APPR" : "Approval Voting",
		"FPTP" : "First Past the Post / Winner Takes All",
		"INST" : "Instant Runoff / Preferential Voting",
		"ALL"  : "Run Every Simulation"
		}

	run_again = "Y"
	while run_again in ('Y', 'YES'):
		for option in OPTION:
			print(option + ": " + OPTION[option])

		while(mode:=input("Enter tallying method: ").upper()) not in OPTION: 
			pass

		tally_votes(mode)

		run_again = input("Run again? (y/n): ").upper()

if __name__ == "__main__":
	run()
