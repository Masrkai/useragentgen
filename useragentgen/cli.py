import argparse
from useragentgen import generate_many

def main():
    parser = argparse.ArgumentParser(description="Generate random User-Agent strings.")
    parser.add_argument("-b", "--browser", type=str, help="Specify browser (chrome, firefox, safari, edge, opera)")
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of User-Agent strings to generate")
    args = parser.parse_args()

    try:
        user_agents = generate_many(args.count, args.browser)
        for ua in user_agents:
            print(ua)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
