# Desjardins importer for Firefly III

A small Docker-based parser that converts Desjardins credit card PDF statements into a CSV format suitable for Firefly III Data Importer.

## What it does

- Reads Desjardins credit card PDF statements
- Extracts transaction date, description, location, and amount
- Converts credits and payments to negative amounts
- Handles December/January year rollover
- Separates description and location using PDF column coordinates
- Outputs a Firefly III-friendly CSV

## Tested with

This was tested with Desjardins Odyssey World Elite Mastercard PDF statements.

Other Desjardins cards may use different PDF layouts and may require coordinate adjustments.

## Output format

```csv
date,description,location,amount
2026-07-10,COSTCO ESSENCE W516,QUEBEC QC,74.70
2026-07-31,PAIEMENT CAISSE,,-5163.32
```

## Disclaimer

This project was created for personal use. Use at your own risk. Always verify the generated CSV before importing data into Firefly III. This parser was created for personal use with Desjardins credit card PDF statements and Firefly III Data Importer. It may not work with all Desjardins statement formats. Always review the generated CSV before importing into Firefly III. Use at your own risk.

## Affiliation and copyright notice

This project is an independent personal project.

The project maintainer is not affiliated with, sponsored by, endorsed by, or connected to the Firefly III project, the Firefly III team, Desjardins, or any related organization.

This tool is intended only to help users convert their own legally obtained personal PDF statements into CSV files for personal use with Firefly III Data Importer.

No Desjardins statement templates, logos, branding assets, proprietary documentation, or copyrighted bank materials are included in this repository. Users should not upload or share real bank statements, account information, card numbers, personal information, or copyrighted statement content.

If any project name, reference, or documentation creates confusion or appears to infringe on someone else's rights, please open an issue so it can be corrected.
``

## AI assistance disclosure

This project was created with AI assistance.

The parser was developed iteratively using Microsoft Copilot to help write, debug, and refine the Python code. The final behavior was tested manually against real Desjardins PDF statements by the project maintainer.

AI assistance was used for:

- Drafting and refactoring Python code
- Troubleshooting PDF text extraction issues
- Comparing PDF word coordinates
- Improving the description/location column split
- Writing documentation and project notes

The project maintainer reviewed, tested, and validated the output before publishing. Users should still review generated CSV files before importing them into Firefly III.
``
