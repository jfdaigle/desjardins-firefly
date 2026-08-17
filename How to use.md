# How to use

## Installation

### 1. Download the project

Download or clone this repository to your computer or NAS.

### 2. Create the required folders

The folder structure should look like this:

desjardins-firefly-parser/

  -parser.py
  
  -Dockerfile
  
  -compose.yaml
  
  input/
  
  output/

### 3. Add your PDF statement

Place your Desjardins PDF statement inside the input folder.

### 4. Build and run the container

If you are using Docker Compose, run:

```docker compose up --build```

The parser will:

- Read the PDF from the input folder

- Extract the transactions

- Create a CSV file in the output folder

- Write a log file and status file

### 5. Check the output

After the container finishes, check the output folder.

You should see files like:

├── statement.csv

├── converter.log

└── last_run.txt

### 6. Review the CSV

Before importing into Firefly III, always open the CSV and review:

Transaction dates

Descriptions

Locations

Amounts

Credits and payments as negative values

### 7. Import into Firefly III

Use Firefly III Data Importer and map the CSV columns as needed.

### NOTE

The container is expected to stop after the parser finishes. This is normal because the parser runs as a one-time conversion job, not as a long-running service.
