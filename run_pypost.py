import sys
from pathlib import Path
from modules.pypost import PyPost


def main():
	if len(sys.argv) < 2:
		print("Usage:")
		print("  python3 run_pypost.py --submit letter_name (without .txt)")
		print("  python3 run_pypost.py --send_pending_letters")
		sys.exit(1)

	flag = sys.argv[1]
	pypost = PyPost()

	if flag == "--submit":
		if len(sys.argv) != 3:
			print("Usage: python3 run_pypost.py --submit letter_name (without .txt)")
			sys.exit(1)
		letter_name = sys.argv[2]
		letter_path = f"LettersToSend/{letter_name}.txt"
		letter_id = pypost.submit_letter(letter_path)
		if letter_id:
			print(f"Letter submitted successfully! Letter ID: {letter_id}:{letter_name}.txt")
		else:
			print("Failed to submit letter.")
		# Delete the submitted letter file
		try:
			Path(letter_path).unlink(missing_ok=True)
			print(f"Deleted file: {letter_path}")
		except Exception as e:
			print(f"Could not delete file {letter_path}: {e}")
	elif flag == "--send_pending_letters":
		sent_letters_ids = pypost.send_pending_letters()
		if sent_letters_ids:
			print(f"Letters sent successfully!: \n{', '.join(sent_letters_ids)}")
		else:
			print("No pending letters sent.")
	else:
		print("Unknown flag. Use --submit or --send_pending_letters.")

if __name__ == "__main__":
	main()
