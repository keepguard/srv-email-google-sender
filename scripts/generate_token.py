
from google_auth_oauthlib.flow import InstalledAppFlow
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate Gmail API token.json")
    parser.add_argument("--client-secrets", required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--scopes", nargs="+", default=["https://www.googleapis.com/auth/gmail.send"])
    args = parser.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(args.client_secrets, args.scopes)
    creds = flow.run_local_server(port=0)

    with open(args.token_file, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(f"✅ Token saved to {args.token_file}")

if __name__ == "__main__":
    main()
