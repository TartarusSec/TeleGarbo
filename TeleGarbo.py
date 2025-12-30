import random
import time
import requests
import argparse
import re


# ------------------ FILE HELPERS ------------------

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return [line.strip() for line in file if line.strip()]


def clean_business_name(name):
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "", name)
    return name


# ------------------ EMAIL GENERATION ------------------

def generate_random_email(first_names_file, last_names_file, business_names_file, extensions_file):
    first_names = read_file(first_names_file)
    last_names = read_file(last_names_file)
    business_names = read_file(business_names_file)
    extensions = read_file(extensions_file)

    first_name = random.choice(first_names).lower()
    last_name = random.choice(last_names).lower()

    # 50/50: initial+last OR first.last
    if random.choice([True, False]):
        username = f"{first_name[0]}{last_name}"   # jsmith
    else:
        username = f"{first_name}.{last_name}"     # john.smith

    business = clean_business_name(random.choice(business_names))
    extension = random.choice(extensions)

    return f"{username}@{business}.{extension}"


# ------------------ PASSWORD ------------------

def get_random_word(password_file_path):
    words = read_file(password_file_path)
    return random.choice(words)


# ------------------ TELEGRAM ------------------

def send_to_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["result"]["message_id"]
    except Exception as e:
        print("Telegram send error:", e)
        return None


def delete_telegram_message(bot_token, chat_id, message_id):
    url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Delete error ({message_id}):", e)
        return False


# ------------------ MESSAGE ID STORAGE ------------------

def load_last_message_id(path="last_message_id.txt"):
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def save_last_message_id(message_id, path="last_message_id.txt"):
    with open(path, "w") as f:
        f.write(str(message_id))


# ------------------ MAIN LOOP ------------------

def generate_emails_periodically(bot_token, chat_id):

    first_names_file = "first-names.txt"
    last_names_file = "last-names.txt"
    business_names_file = "business-names.txt"
    extensions_file = "extension.txt"
    password_file = "rockyou.txt"

    while True:
        fake_email = generate_random_email(
            first_names_file,
            last_names_file,
            business_names_file,
            extensions_file
        )

        password = get_random_word(password_file)

        message = (
            "Nouvelle connexion :\n"
            f"ei : {fake_email}\n"
            f"pa : {password}"
        )

        message_id = send_to_telegram(bot_token, chat_id, message)

        if message_id is not None:
            print("\n--- SENT MESSAGE ---")
            print(f"Email      : {fake_email}")
            print(f"Password   : {password}")
            print(f"Message ID : {message_id}")

            last_id = load_last_message_id()

            if last_id is None:
                print("Status     : First message saved")

            elif message_id > last_id + 1:
                print(f"Status     : ⚠️ ID SKIPPED ({last_id} → {message_id})")

                for skipped_id in range(last_id + 1, message_id):
                    deleted = delete_telegram_message(bot_token, chat_id, skipped_id)
                    if deleted:
                        print(f"Deleted skipped ID : {skipped_id}")
                    else:
                        print(f"Could NOT delete ID: {skipped_id}")

            else:
                print("Status     : ID OK")

            save_last_message_id(message_id)
            print("---------------------\n")

        interval = random.randint(2 * 1, 2 * 3)
        print(f"Next run in {interval / 60:.2f} minutes...\n")
        time.sleep(interval)


# ------------------ ENTRY POINT ------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate fake emails, send to Telegram, detect and delete skipped message IDs"
    )
    parser.add_argument("-t", "--token", required=True, help="Telegram Bot Token")
    parser.add_argument("-c", "--chat", required=True, help="Telegram Chat ID")

    args = parser.parse_args()
    generate_emails_periodically(args.token, args.chat)


if __name__ == "__main__":
    main()
