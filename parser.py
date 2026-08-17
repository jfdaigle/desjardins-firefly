import pdfplumber
import csv
import re
from pathlib import Path
from datetime import datetime

VERSION = "2.0"

INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")
OUTPUT_DIR.mkdir(exist_ok=True)

LOGFILE = OUTPUT_DIR / "converter.log"


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = "[" + timestamp + "] " + message
    print(entry)

    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def write_status(status, pdf_name="", csv_file="", transactions=0):
    status_file = OUTPUT_DIR / "last_run.txt"

    with open(status_file, "w", encoding="utf-8") as f:
        run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("Run Date: " + run_date + "\n\n")
        f.write("Status: " + status + "\n")

        if pdf_name:
            f.write("PDF: " + pdf_name + "\n")

        if csv_file:
            f.write("CSV: " + csv_file + "\n")

        f.write("Transactions Parsed: " + str(transactions) + "\n")


def is_two_digit_number(value):
    return re.match(r"^\d{2}$", value) is not None


def is_amount(value):
    return re.match(r"^\d[\d ]*,\d{2}(CR)?$", value) is not None


def is_integer(value):
    return re.match(r"^\d+$", value) is not None


def is_bonus_value(value):
    return re.match(r"^\d+,\d{2}$", value) is not None


def amount_to_float(value):
    credit = value.endswith("CR")

    value = value.replace("CR", "")
    value = value.replace(" ", "")
    value = value.replace(",", ".")

    amount = float(value)

    if credit:
        amount = amount * -1

    return amount


def group_words_by_line(words):
    lines = []

    words = sorted(words, key=lambda w: (w["top"], w["x0"]))

    for word in words:
        found_line = None

        for line in lines:
            if abs(word["top"] - line["top"]) <= 3:
                found_line = line
                break

        if found_line is None:
            lines.append({
                "top": word["top"],
                "words": [word]
            })
        else:
            found_line["words"].append(word)

    for line in lines:
        line["words"] = sorted(line["words"], key=lambda w: w["x0"])

    return lines


def extract_statement_date(pdf):
    statement_month = None
    statement_year = None

    for page in pdf.pages:
        text = page.extract_text()

        if not text:
            continue

        match = re.search(
            r"DATE DU RELEVÉ\s+Jour\s+\d{2}\s+Mois\s+(\d{2})\s+Année\s+(\d{4})",
            text
        )

        if match:
            statement_month = int(match.group(1))
            statement_year = int(match.group(2))
            break

    return statement_month, statement_year


def find_amount(words):
    texts = [w["text"] for w in words]

    for i in range(len(texts) - 1, -1, -1):
        current = texts[i]

        if is_amount(current):
            if i > 0 and is_integer(texts[i - 1]):
                amount_text = texts[i - 1] + " " + current
                return i - 1, amount_text

            return i, current

    return None, None


def split_description_location(words):
    DESCRIPTION_X_MIN = 210
    DESCRIPTION_X_MAX = 335

    LOCATION_X_MIN = 335
    LOCATION_X_MAX = 425

    description_words = []
    location_words = []

    for word in words:
        x0 = word["x0"]

        if DESCRIPTION_X_MIN <= x0 < DESCRIPTION_X_MAX:
            description_words.append(word)

        elif LOCATION_X_MIN <= x0 < LOCATION_X_MAX:
            location_words.append(word)

    description = " ".join(w["text"] for w in description_words)
    location = " ".join(w["text"] for w in location_words)

    return description.strip(), location.strip()


def parse_transaction(words, statement_month, statement_year):
    texts = [w["text"] for w in words]

    if len(texts) < 6:
        return None

    if not is_two_digit_number(texts[0]):
        return None

    if not is_two_digit_number(texts[1]):
        return None

    if not is_two_digit_number(texts[2]):
        return None

    if not is_two_digit_number(texts[3]):
        return None

    transaction_day = texts[0]
    transaction_month = texts[1]

    amount_index, amount_text = find_amount(words)

    if amount_text is None:
        return None

    try:
        amount = amount_to_float(amount_text)
    except Exception:
        return None

    middle_words = words[4:amount_index]

    if len(middle_words) >= 2:
        last_text = middle_words[-1]["text"]
        previous_text = middle_words[-2]["text"]

        if last_text == "%" and is_bonus_value(previous_text):
            middle_words = middle_words[:-2]

    description, location = split_description_location(middle_words)

    if statement_year is None:
        statement_year = datetime.now().year

    transaction_year = statement_year

    if statement_month is not None:
        if int(transaction_month) > statement_month:
            transaction_year = statement_year - 1

    date_text = (
        str(transaction_year)
        + "-"
        + transaction_month
        + "-"
        + transaction_day
    )

    return [
        date_text,
        description,
        location,
        amount
    ]


try:
    log("====================================")
    log("Desjardins parser started")

    log("Parser version: " + VERSION)
    
    pdfs = list(INPUT_DIR.glob("*.pdf"))

    log("PDFs found: " + str(len(pdfs)))

    if not pdfs:
        log("No PDFs found")
        write_status(status="NO PDFS FOUND")

    for pdf_file in pdfs:
        log("Processing " + pdf_file.name)

        transactions = []
        lines_processed = 0

        with pdfplumber.open(pdf_file) as pdf:
            statement_month, statement_year = extract_statement_date(pdf)

            log("Statement month: " + str(statement_month))
            log("Statement year: " + str(statement_year))

            for page in pdf.pages:
                words = page.extract_words(
                    x_tolerance=1,
                    y_tolerance=3,
                    keep_blank_chars=False
                )

                lines = group_words_by_line(words)

                for line in lines:
                    lines_processed = lines_processed + 1

                    transaction = parse_transaction(
                        line["words"],
                        statement_month,
                        statement_year
                    )

                    if transaction:
                        transactions.append(transaction)

        output_csv = OUTPUT_DIR / (pdf_file.stem + ".csv")

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow([
                "date",
                "description",
                "location",
                "amount"
            ])

            writer.writerows(transactions)

        log("Lines processed: " + str(lines_processed))
        log(
            "Created "
            + output_csv.name
            + " with "
            + str(len(transactions))
            + " transactions"
        )

        write_status(
            status="SUCCESS",
            pdf_name=pdf_file.name,
            csv_file=output_csv.name,
            transactions=len(transactions)
        )

    log("Parser finished")

except Exception as e:
    log("ERROR: " + str(e))

    write_status(
        status="ERROR - " + str(e)
    )

    raise