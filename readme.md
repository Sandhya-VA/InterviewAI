# Resume Parsing using SpaCy

This project extracts skills from resumes using SpaCy's NLP capabilities and an entity ruler with a predefined skill pattern.

## Features
- Preprocesses text by removing hyperlinks and stopwords.
- Extracts skills using SpaCy's Named Entity Recognition (NER) with custom patterns.
- Reads and processes PDF resumes using PyMuPDF.

## Installation
### Prerequisites
Ensure you have Python installed (recommended version: 3.8+) and python -m spacy download en_core_web_md installed.

### Install dependencies
Run the following command to install the required libraries:
```sh
pip install -r requirements.txt
