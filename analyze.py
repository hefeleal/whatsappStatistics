#!/usr/bin/python3
# coding=utf-8

import re
import argparse
import collections
import datetime

class Message():
	def __init__(self, time, who, what, is_meta, is_media, is_deleted, is_contact, is_location):
		self.time = time
		self.who = who
		self.what = what
		self.is_meta = is_meta
		self.is_media = is_media
		self.is_deleted = is_deleted
		self.is_contact = is_contact
		self.is_location = is_location

	def is_special_message(self):
		return self.is_meta or self.is_media or self.is_deleted or self.is_contact or self.is_location

	def get_time_string(self):
		return datetime.datetime.strftime(self.time, "%d.%m.%y, %H:%M")

	def __str__(self):
		return self.get_time_string() + ": " + self.who + " - " + self.what

# parses the text file and returns an array of messages
# Expects a German WhatsApp chat text file that was
# exported on Android. Parsing in other languages will
# fail and when exporting on iOS, the format might be
# different.
def parse_file(filename):
	with open(filename, "r") as f:
		raw_content = f.readlines()
	msgs = []
	for c in raw_content:
		regex = re.findall("([0-3][0-9]\.[0-1][0-9]\.[0-9][0-9], [0-2][0-9]:[0-5][0-9]) - (.*?)(: .*)?\n", c, re.S)
		if len(regex) == 0:
			msgs[len(msgs)-1].what += "\n" + c[:-1]
		elif regex[0][2] == "":
			msgs.append(Message(datetime.datetime.strptime(regex[0][0], "%d.%m.%y, %H:%M"), "xxx", regex[0][1], True, False, False, False, False))
		else:
			is_media = False
			is_deleted = False
			is_contact = False
			is_location = False
			if regex[0][2][2:] == "<Medien weggelassen>":
				is_media = True
			elif regex[0][2][2:] == "Diese Nachricht wurde gelöscht":
				is_deleted = True
			elif regex[0][2][-22:] == ".vcf (Datei angehängt)":
				is_contact = True
			elif regex[0][2][2:] == "Live-Standort wird geteilt" or regex[0][2][2:36] == "Standort: https://maps.google.com/":
				is_location = True
			msgs.append(Message(datetime.datetime.strptime(regex[0][0], "%d.%m.%y, %H:%M"), regex[0][1], regex[0][2][2:], False, is_media, is_deleted, is_contact, is_location))
	return msgs

# prints for how many days the chat spans
def print_total_days(msgs):
	diff = msgs[len(msgs) - 1].time - msgs[0].time
	print(diff.days, "total days")

# prints out on how many days no messages (including media,
# deleted messages, contacts and locations) were sent
def print_number_of_days_without_messsages(msgs):
	unique_days = set()
	for m in msgs:
		if not m.is_meta:
			date = datetime.datetime.strftime(m.time, "%d.%m.%y")
			unique_days.add(date)
	total_days = msgs[len(msgs) - 1].time - msgs[0].time
	no_msgs = total_days.days - len(unique_days)
	print("On {} days ({:1.1f}%) no messages were sent".format(no_msgs, (no_msgs / total_days.days) * 100))

# prints a ranking of users who changed their WhatsApp
# security number most often (i.e. switched phones)
def print_securitynumber_ranking(msgs):
	ranking = collections.Counter()
	for m in msgs:
		if m.is_meta:
			found_user = re.findall("Die Sicherheitsnummer von (.*) hat sich geändert", m.what, re.S)
			if len(found_user) > 0:
				ranking[found_user[0]] += 1
	print("Security Number Ranking:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} - {}".format(i, r[1], r[0]))
		i += 1

# prints all meta messages, e.g. user was added/removed from group
# changed security number, changed title, ...
def print_meta_messages(msgs):
	print("Meta messages:")
	total_count = 0
	for m in msgs:
		if m.is_meta:
			print(m.get_time_string(), m.what)
			total_count += 1
	print("In total", total_count, "meta messages")

# prints how many messages (including media, deleted messages,
# contacts and locations) were sent during each hour of the day
def print_messages_by_time(msgs):
	total_count = 0
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_meta:
			ranking[m.time.hour] += 1
			total_count += 1
	print("Messages by time:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} ({:1.1f}%) - {}:00 Uhr - {:02}:00 Uhr".format(i, r[1], (r[1]/total_count)*100, r[0], (int(r[0])+1)%24))
		i += 1

# prints how many messages (including media, deleted messages,
# contacts and locations) were sent for each day of the week
def print_messages_by_weekday(msgs):
	total_count = 0
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_meta:
			ranking[m.time.weekday()] += 1
			total_count += 1
	weekday_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
	print("Messages by weekday:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} ({:1.1f}%) - {}".format(i, r[1], (r[1]/total_count)*100, weekday_names[r[0]]))
		i += 1

# prints how many messages there are in total, including
# media, deleted messages, contacts and locations
def print_total_messages(msgs):
	ctr = 0
	for m in msgs:
		if not m.is_meta:
			ctr += 1
	print(ctr, "total messages")

# prints how many words there are in total, but only in 
# normal text messages (no media, ...)
def print_total_words(msgs):
	ctr = 0
	for m in msgs:
		if not m.is_special_message():
			ctr += len(re.findall("\w+", m.what, re.S))
	print(ctr, "total words")

# prints how many letters there are in total, but only in 
# normal text messages (no media, ...)
def print_total_letters(msgs):
	ctr = 0
	for m in msgs:
		if not m.is_special_message():
			ctr += len(m.what)
	print(ctr, "total letters")

# prints a ranking of users who sent the most messages
# (including media, deleted messages, contacts and locations)
# distribution: https://en.wikipedia.org/wiki/Power_law
def print_user_ranking(msgs):
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_meta:
			ranking[m.who] += 1
	print("User Ranking (most total messages):")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} - {}".format(i, r[1], r[0]))
		i += 1

# prints a ranking of which digit (1-9) is most often the very
# first digit of a number
# distribution: https://en.wikipedia.org/wiki/Benford%27s_law
def print_first_digit_distribution(msgs):
	total_count = 0
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_meta:
			numbers = re.findall("[1-9][0-9]*", m.what, re.S)
			for n in numbers:
				ranking[n[:1]] += 1
				total_count += 1
	print("First digit distribution:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} ({:1.1f}%) - Ziffer {}".format(i, r[1], (r[1]/total_count)*100, r[0]))
		i += 1
	print("In total", total_count, "numbers")

# prints a ranking of days, on which the most messages were sent
# (including media, deleted messages, contacts and locations)
def print_day_ranking(msgs):
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_meta:
			date = datetime.datetime.strftime(m.time, "%d.%m.%y")
			ranking[date] += 1
	print("Day Ranking:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} messages on {}".format(i, r[1], r[0]))
		i += 1

# prints a ranking of users who sent the most deleted messages
def print_deleted_messages_ranking(msgs):
	print_word_ranking(msgs, "Diese Nachricht wurde gelöscht")

# prints a ranking of users who sent the most media messages
def print_medias_ranking(msgs):
	print_word_ranking(msgs, "<Medien weggelassen>")

# prints a ranking of users who sent the most messages that contain
# a specified word or phrase. This function considers media- and deleted-,
# contact- and location- messages on purpose!
def print_word_ranking(msgs, word):
	total_count = 0
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_meta:
			if word.lower() in m.what.lower():
				ranking[m.who] += 1
				total_count += 1
	print("Ranking for '" + word + "':")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} - {}".format(i, r[1], r[0]))
		i += 1
	print("In total", total_count, "messages with '" + word + "'.")

# prints a ranking of how often each letter is used, but only in 
# normal text messages (no media, ...). This function does not
# differentiate between upper and lower case
def print_letter_count(msgs):
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_special_message():
			for letter in m.what:
				ranking[letter.lower()] += 1
	print("Letter Count:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} - {}".format(i, r[1], r[0]))
		i += 1

# prints a ranking of how often each word is used, but only in 
# normal text messages (no media, ...). This function does not
# differentiate between upper and lower case
def print_word_count(msgs):
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_special_message():
			words = re.findall("\w+", m.what, re.S)
			for w in words:
				ranking[w.lower()] += 1
	print("Word Count:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} - {}".format(i, r[1], r[0]))
		i += 1

# prints a ranking of users who get @-mentioned most often,
# but only in normal text messages (no media, ...).
def print_most_mentions(msgs):
	total_count = 0
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_special_message():
			refs = re.findall("@[0-9][0-9][0-9][0-9][0-9]+", m.what, re.S)
			for r in refs:
				ranking[r] += 1
				total_count += 1
	print("Most @-mentions:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} - {}".format(i, r[1], r[0]))
		i += 1
	print("In total", total_count, "@-mentions")

# prints a ranking of the most used hashtags,
# but only in normal text messages (no media, ...).
def print_hashtag_ranking(msgs):
	total_count = 0
	ranking = collections.Counter()
	for m in msgs:
		if not m.is_special_message():
			hashtags = re.findall("#(\w+)", m.what, re.S)
			for h in hashtags:
				ranking[h] += 1
				total_count += 1
	print("Most hashtags:")
	i = 1
	for r in ranking.most_common():
		print("{:02}. {} - #{}".format(i, r[1], r[0]))
	print("In total", total_count, "hashtags")

# prints the longest message
def print_longest_message(msgs):
	longest_count = 0
	longest_message = ""
	for m in msgs:
		if not m.is_special_message():
			if len(m.what) > longest_count:
				longest_count = len(m.what)
				longest_message = m.what
	print("Longest message:")
	print(longest_message)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("file", help="file to parse")
	parser.add_argument("-td", "--total-days", help="print total number of days", action="store_true")
	parser.add_argument("-dwm", "--days-without-messages", help="print number of days without messages", action="store_true")
	parser.add_argument("-tm", "--total-messages", help="print how many messags there are in total", action="store_true")
	parser.add_argument("-tw", "--total-words", help="print how many words there are in total", action="store_true")
	parser.add_argument("-tl", "--total-letters", help="print how many letters there are in total", action="store_true")
	parser.add_argument("-ur", "--user-ranking", help="print a ranking of users who sent the most messages", action="store_true")
	parser.add_argument("-wr", "--word-ranking", help="print a ranking of users who sent the most messages that contain a specified word or phrase", dest="search_term", default=None)
	parser.add_argument("-mr", "--medias-ranking", help="print a ranking of users who sent the most media messages", action="store_true")
	parser.add_argument("-dmr", "--deleted-messages-ranking", help="print a ranking of users who sent the most deleted messages", action="store_true")
	parser.add_argument("-mt", "--messages-by-time", help="print how many messages were sent during each hour of the day", action="store_true")
	parser.add_argument("-mw", "--messages-by-weekday", help="print how many messages were sent for each day of the week", action="store_true")
	parser.add_argument("-lc", "--letter-count", help="print a ranking of how often each letter is used", action="store_true")
	parser.add_argument("-wc", "--word-count", help="print a ranking of how often each word is used", action="store_true")
	parser.add_argument("-sr", "--securitynumber-ranking", help="print a ranking of users who changed their WhatsApp security number most often", action="store_true")
	parser.add_argument("-mm", "--meta-messages", help="print all meta messages", action="store_true")
	parser.add_argument("-fd", "--first-digit-distribution", help="print a ranking of which digit (1-9) is most often the very first digit of a number", action="store_true")
	parser.add_argument("-dr", "--day-ranking", help="print a ranking of days, on which the most messages were sent", action="store_true")
	parser.add_argument("-mme", "--most-mentions", help="print a ranking of users who get @-mentioned most often", action="store_true")
	parser.add_argument("-hr", "--hashtag-ranking", help="print a ranking of the most used hashtags", action="store_true")
	parser.add_argument("-lm", "--longest-message", help="print the longest message", action="store_true")
	args = parser.parse_args()
	msgs = parse_file(args.file)
	if args.total_days:
		print_total_days(msgs)
		print()
	if args.days_without_messages:
		print_number_of_days_without_messsages(msgs)
		print()
	if args.total_messages:
		print_total_messages(msgs)
		print()
	if args.total_words:
		print_total_words(msgs)
		print()
	if args.total_letters:
		print_total_letters(msgs)
		print()
	if args.user_ranking:
		print_user_ranking(msgs)
		print()
	if args.search_term != None:
		print_word_ranking(msgs, args.search_term)
		print()
	if args.medias_ranking:
		print_medias_ranking(msgs)
		print()
	if args.deleted_messages_ranking:
		print_deleted_messages_ranking(msgs)
		print()
	if args.messages_by_time:
		print_messages_by_time(msgs)
		print()
	if args.messages_by_weekday:
		print_messages_by_weekday(msgs)
		print()
	if args.letter_count:
		print_letter_count(msgs)
		print()
	if args.word_count:
		print_word_count(msgs)
		print()
	if args.securitynumber_ranking:
		print_securitynumber_ranking(msgs)
		print()
	if args.meta_messages:
		print_meta_messages(msgs)
		print()
	if args.first_digit_distribution:
		print_first_digit_distribution(msgs)
		print()
	if args.day_ranking:
		print_day_ranking(msgs)
		print()
	if args.most_mentions:
		print_most_mentions(msgs)
		print()
	if args.hashtag_ranking:
		print_hashtag_ranking(msgs)
		print()
	if args.longest_message:
		print_longest_message(msgs)
		print()
