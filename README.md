# Document Generator

This is used to generate the specifications from a CA (Capability Architect) database in Markdown form.

Since CA uses a Microsoft Access Database (`.accdb`) which is a flat-file database, the `.accdb` file can be moved into this repository, where it's data can be extracted.

## Setup

This generator only works on Windows due to a lack of support for `.accdb` files which is what CA uses.

Assuming you are on windows and have python + pip installed, run the following commands in command prompt to set up the dependencies.

```sh
# Install virtual environment
pip install venv

# Create virtual environment
python -m venv env

# Start virtual environment
.\env\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

## Creating Documentation

To create the documentation, run the following command, which will save the updated spec in `md-specs/`.

Note the `<database name>` is an optional command line argument which defaults to `database.accdb`.

Currently `database.accdb` is the database to be used for SS8, whilst `database2.accdb` is the one used for SS7.

```
python main.py <database name>
```

## Database Structure [SUBJECT TO CHANGE]

The requirements can be found in "System Requirement" categorised by department.

The table below explains the metadata.

| Metadata                | Purpose                                          |
| ----------------------- | ------------------------------------------------ |
| **Subsystem**           | Which team is responsible for each requirement   |
| **Verification Method** | How will we test that this requirement is passed |
| **Origin**              | Where did this requirement come from?            |
| **Priority**            | When do we need this complete by?                |
