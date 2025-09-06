import sys
from modules.pypost import PyPost

def main():
	if len(sys.argv) != 2:
		print("Usage: python3 run_pypost.py letter_name (without .txt)")
		sys.exit(1)
	letter_path = "/LettersToSend/" + sys.argv[1] + ".txt"
	pypost = PyPost()
	letter_id = pypost.submit_letter(letter_path)
	if letter_id:
		print(f"Letter submitted successfully! Letter ID: {letter_id}")
	else:
		print("Failed to submit letter.")

if __name__ == "__main__":
	main()
