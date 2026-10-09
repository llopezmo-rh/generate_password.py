#!/usr/bin/python3

import argparse
import secrets
import shutil
import string
import subprocess
import sys


NON_ALPHANUMERIC_SET = "!._#%&$@*"
DEFAULT_LENGTH = 10
# The password created by this script fullfills the following requirements:
# 1. The first and last characters are alphanumerical.
# 2. Among the rest of the characters there must be at least a number and a
#    non-alphanumercal character.
# Consequence: the length must be at least 4. Change the "constant" below only
# if the logic of the script is changed.
MIN_LENGTH = 4


def generate_secure_random_string(
	length: int,
	min_numerical: int = 0,
	min_non_alphanumeric: int = 0,
	max_numerical: int | None = None,
	max_non_alphanumeric: int | None = None,
	non_alphanumeric_set: str = NON_ALPHANUMERIC_SET
) -> str:
	"""
	Generates a cryptographically secure random string with count constraints.
	"""
	# Value validations (domain invariants)
	if length < 0:
		raise ValueError("Length cannot be negative")
	if min_numerical < 0 or min_non_alphanumeric < 0:
		raise ValueError("Minimum requirements cannot be negative")
	if max_numerical is not None and max_numerical < 0:
		raise ValueError("Maximum numerical requirement cannot be negative")
	if max_non_alphanumeric is not None and max_non_alphanumeric < 0:
		raise ValueError("Maximum non-alphanumeric requirement cannot be negative")
	if min_numerical + min_non_alphanumeric > length:
		raise ValueError("Sum of minimum requirements exceeds total length")
	if len(non_alphanumeric_set) == 0:
		raise ValueError("Non-alphanumeric set cannot be an empty string")
	if max_numerical is not None and max_numerical < min_numerical:
		raise ValueError("Max numerical requirement cannot be lower than minimum")
	if max_non_alphanumeric is not None and max_non_alphanumeric < min_non_alphanumeric:
		raise ValueError("Max non-alphanumeric requirement cannot be lower than minimum")

	# Generate required minimum characters securely using explicit loops.
	# Lists used instead of strings because lists are mutable. Adding new items to
	# them implies a lower performance impact
	numerical_chars = []
	for _ in range(min_numerical):
		selected_char = secrets.choice(string.digits)
		numerical_chars.append(selected_char)

	non_alphanumeric_chars = []
	for _ in range(min_non_alphanumeric):
		selected_char = secrets.choice(non_alphanumeric_set)
		non_alphanumeric_chars.append(selected_char)

	# Initialize character type counts
	count_numerical = min_numerical
	count_non_alphanumeric = min_non_alphanumeric

	# Calculate remaining characters needed
	remaining_length = length - (min_numerical + min_non_alphanumeric)
	remaining_chars = []

	for _ in range(remaining_length):
		# Dynamically construct available character pool respecting max bounds
		available_choices = string.ascii_letters
		if max_numerical is None or count_numerical < max_numerical:
			available_choices += string.digits
		if max_non_alphanumeric is None or \
			count_non_alphanumeric < max_non_alphanumeric:
			available_choices += non_alphanumeric_set

		next_char = secrets.choice(available_choices)
		if next_char in string.digits:
			count_numerical += 1
		elif next_char in non_alphanumeric_set:
			count_non_alphanumeric += 1

		remaining_chars.append(next_char)

	# Combine all generated characters and shuffle securely
	full_character_list = numerical_chars + non_alphanumeric_chars + remaining_chars
	secrets.SystemRandom().shuffle(full_character_list)

	# Convert into string and return
	return "".join(full_character_list)

def copy_to_clipboard(text: str) -> None:
	"""
	Copy the given text to the GNU/Linux system clipboard.
	Supports Wayland (wl-copy) and X11 (xclip, xsel).
	"""
	if shutil.which("wl-copy"):
		command = ["wl-copy"]
	elif shutil.which("xclip"):
		command = ["xclip", "-selection", "clipboard"]
	elif shutil.which("xsel"):
		command = ["xsel", "--clipboard", "--input"]
	else:
		raise FileNotFoundError("No clipboard software in the system")

	subprocess.run(command, input=text.encode("utf-8"), check=True)


if __name__ == "__main__":
	# Parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--clipboard", action='store_true',
		help="Copy password to clipboard")
	# nargs="?" to make optional the positional argument
	parser.add_argument("length", action="store", type=int, nargs="?",
		default=DEFAULT_LENGTH, help="Password length")
	args = parser.parse_args()

	# Validate arguments
	if args.length < MIN_LENGTH:
		print(f"Error: length is too short. Minimum required: {MIN_LENGTH}",
			file=sys.stderr)
		sys.exit(22)

	# Generate strings
	first_character = generate_secure_random_string(1, max_non_alphanumeric=0)
	last_character = generate_secure_random_string(1, max_non_alphanumeric=0)
	middle_length = args.length - 2
	middle_string = generate_secure_random_string(middle_length,
		min_numerical=1, min_non_alphanumeric=1)
	
	# Print password
	password = first_character + middle_string + last_character
	print(password)
	
	# Copy to clipboard if the corresponding option has been chosen
	if args.clipboard:
		try:
			copy_to_clipboard(password)
			print("\nPassword copied into clipboard!")
		except FileNotFoundError:
			print("\nThe password could not be copied to the operating-system"
				"clipboard because none of the following applications seem to "
				"be installed:\n- wl-copy.\n- xclip.\n- xsel.",
				file=sys.stderr)
			sys.exit(1)
			
