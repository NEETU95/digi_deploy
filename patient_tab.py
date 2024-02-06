from PyPDF2 import PdfReader
import os
import spacy
import re
import pycountry
import json
import pandas as pd
import fitz
import stanza
from stanza.pipeline.core import DownloadMethod


#from parent import mother_llt, all_text, nlp, nlp_1

# weekly_reader = PdfReader('Weekly Literature Hits PDF-plante.pdf')
# source_file_reader = PdfReader('Plante MM.pdf')
# doc = fitz.open("Plante MM.pdf")
# # weekly_reader = PdfReader('Weekly literature hits PDF.pdf')
# weekly_reader_num_pages = len(weekly_reader.pages)
#
# source_file_num_pages = len(source_file_reader.pages)
# weekly_text = ""
# all_text = ""
# nlp = spacy.load("en_core_web_sm")
# nlp_1 = stanza.Pipeline('en', package='mimic', processors={'ner': 'i2b2'}, download_method=DownloadMethod.REUSE_RESOURCES)
# first_page = source_file_reader.pages[0]
# first_page_text = first_page.extract_text()
# # Loop through all pages and extract text
#  # open a document
# for page_num in range(doc.page_count):
#     page = doc[page_num]
#     text = page.get_text()
#     all_text += text
# for page_num in range(weekly_reader_num_pages):
#     page = weekly_reader.pages[page_num]
#     text = page.extract_text()
#     weekly_text += text
# meta = source_file_reader.metadata
#print(all_text)
def get_patient_text(source_text, en_core, bcd5r):
    all_text = source_text
    nlp_1 = bcd5r
    nlp = en_core

    report_to_discussion = ""
    first_three_lines = ""
    abstract_keywords = ["Introduction", "Abstract", "INTRODUCTION", "ABSTRACT"]
    case_keywords = ["Case Presentation", "Case presentation", "Case summary", "Case history", "Case Summary",
                     "Case History", "Case description", "Case Report",
                     "Case report", "CASE", "Case", "CASE REPORT", "CASE DESCRIPTION", "CASE PRESENTATION",
                     "CASE HISTORY", "CASE SUMMARY"]
    found_case_type = None
    text_after_case_type = ""
    all_drug_information =[]
    all_medical_history =[]
    abstract_to_end = ""
    protect_confidentiality = "Yes"
    found_start_line_second = ""
    abstract_to_end_first = ""
    doc = nlp(all_text)
    for keyword in case_keywords:
        if keyword in all_text:
            # print("keyword is presnet")
            found_case_type = keyword
            break
    if "An official website of the United States government" in all_text:
        word_index = doc.text.find("Affiliations")
        word_index_keyword = doc.text.find("Keywords")
        # print(word_index_keyword)
        extracted_text = doc.text[word_index:word_index_keyword]
        # text_lines = text_after_case_type.split('\n')
        first_three_lines = extracted_text
        report_to_discussion = extracted_text
    else:
        abstract_terms = ["Introduction", "Abstract", "INTRODUCTION", "ABSTRACT"]
        count = 0
        found_start_line = -1
        end_line = -1
        searching = ""
        for i, line in enumerate(all_text.split('\n')):
            for searching in abstract_terms:
                if searching in line:
                    # print("yes abstract keyword is present")
                    count += 1
                    found_start_line = i
                    break
        print("found_start_line is", found_start_line)
        # print("count is", count)
        if count > 0 and found_start_line != -1:
            # print("second yes")
            # Extract the found line and the subsequent 7 lines
            extracted_lines_from_abstract = all_text.split('\n')[found_start_line + len(searching):]
            # print(extracted_lines)
            abstract_to_end_first = '\n'.join(extracted_lines_from_abstract)
            #print("abstract to end", abstract_to_end_first)
        count_2 = 0
        for i, line in enumerate(abstract_to_end_first.split('\n')):
            for searching in abstract_terms:
                if searching in line:
                    # print("yes abstract keyword is present second time", line)
                    count_2 += 1
                    print("count is", count_2)
                    found_start_line_second = i
                break
        # print("found_start_line second time is", found_start_line_second)
        # print("count is", count)
        if count_2 > 0 and found_start_line_second != -1:
            # print("second yes")
            # Extract the found line and the subsequent 7 lines
            extracted_lines_from_abstract = abstract_to_end_first.split('\n')[found_start_line:]
            # print(extracted_lines)
            abstract_to_end = '\n'.join(extracted_lines_from_abstract)
            #print("abstract to end from count 2", abstract_to_end)
        else:
            abstract_to_end = abstract_to_end_first

        # print("abstract_to_end", abstract_to_end)

        case_keywords = ["Case Presentation", "Case presentation", "Case summary", "Case history", "Case Summary",
                         "Case History", "Case description", "Case Report",
                         "Case report", "CASE", "Case", "CASE REPORT", "CASE DESCRIPTION", "CASE PRESENTATION",
                         "CASE HISTORY",
                         "CASE SUMMARY"]
        found_case_type = None
        count_for_case = 0
        found_start_line_for_case = -1
        end_line = -1

        print("split of ab_to_end*****", abstract_to_end.split('\n'))
        for i, line in enumerate(abstract_to_end.split("\n")):
            for searching in case_keywords:
                if searching in line:
                    print("Yes case keyword is present")
                    print("line is", line)
                    print("case keyword is", searching)

                    count_for_case += 1
                    print("count_for_case is", count_for_case)
                    if count_for_case == 1:
                        found_start_line_for_case = i
                        print(i)
                    break
            # Stop searching if a keyword is found in the line

            # Assuming you want to store the line index where "Case Report" is found
            if any(keyword in line for keyword in ["Discussion", "Conclusion", "DISCUSSION", "CONCLUSION"]):
                print("line", line)
                print("i", i)
                end_line = i
                break

        print("found_start_line_for_case is", found_start_line_for_case)

        # print("count is", count)

        if count_for_case > 0 and found_start_line_for_case != -1:
            print("second yes")
            # Extract the found line and the subsequent 7 lines
            extracted_lines = abstract_to_end.split('\n')[found_start_line_for_case:(end_line + 1)]
            # print(extracted_lines)
            report_to_discussion = '\n'.join(extracted_lines)
            #print("report to discussion is", report_to_discussion)
            first_three_lines_split = report_to_discussion.split("\n")[:10]
            first_three_lines = '\n'.join(first_three_lines_split)
            # if count > 0:
            #     extracted_text = doc.text[word_index:]
            #     text_lines = extracted_text.split('\n')
            #     first_three_lines = '\n'.join(text_lines[:8])
    # else:
    #     # print("Found case type:", found_case_type)
    #     word_index = doc.text.find(found_case_type)
    #     end_word_index = doc.text.find("Discussion")
    #     # Extract text after the specific word
    #     extracted_text = doc.text[word_index + len(found_case_type):  end_word_index]
    #     text_after_case_type = all_text.split(found_case_type, 1)[-1]
    #     text_lines = extracted_text.split('\n')
    #     report_to_discussion = '\n'.join(text_lines)
    #     first_three_lines_split = report_to_discussion.split("\n")[:10]
    #     first_three_lines = '\n'.join(first_three_lines_split)
    #     print(report_to_discussion)
    previous_lines = []
    text_before_medicine = ""
    text_after_medicine_raw = ""
    products = pd.read_excel("product_names.xlsx")
    # def join_lines(lines):
    #     joined_lines = []
    #     current_line = ""
    #
    #     for line in lines:
    #         if line.endswith('-'):
    #             current_line += line.rstrip('-').rstrip()
    #         else:
    #             current_line += line
    #             joined_lines.append(current_line)
    #             current_line = ""
    #
    #     if current_line:
    #         joined_lines.append(current_line)
    #
    #     return joined_lines

    count_for_drug = 0
    drug_found = ""
    for line_number, line in enumerate(report_to_discussion.split('\n')):
        # Check if medicine has already been found
        if not text_before_medicine:
            for drug in products['product_name']:
                if drug.lower() in line.lower():
                    drug_found = drug.lower()
                    print("found drug is", drug)

                    count_for_drug += 1


                    line_index = line.lower().find(drug.lower())
                    print(line_index)
                    text_line = line[:line_index + len(drug)]
                    #print("text line is......", text_line)
                    # Combine the current line and the previous lines before the medicine
                    text_before_medicine += "\n".join(previous_lines) + "\n" + text_line

                    lines = report_to_discussion.split('\n')[line_number:]
                    #print(lines)
                    # Extract lines after the medicine is found (adjust line_number accordingly)
                    text_after_medicine_raw += "\n".join(lines)

                    # Clear previous_lines for the next iteration
                    previous_lines = []

                    # Stop searching for other drugs in the same line once one is found
                    break

        # If medicine is not found in the current line, store the line in previous_lines
        if not text_before_medicine:
            previous_lines.append(line)

    text_after_medicine = ""
    for line_number, line in enumerate(text_after_medicine_raw.split('\n')):
        if drug_found.lower() in line.lower():
            line_index = line.lower().find(drug_found.lower())
            text_line = line[line_index + len(drug_found):]
            text_after_medicine = text_after_medicine_raw[line_index + len(drug_found):]
            print(text_after_medicine)
            break
    print("****Text Before Medicine*****")
    print(text_before_medicine)
    print("*****\nText After Medicine****")
    print(text_after_medicine)
    # Extract the first three lines
    # print("from another document:", report_to_discussion)

    # print("first three#########", first_three_lines)

    doc = nlp(first_three_lines)

    # First Name
    title = ""
    patient_name = ""
    first_name = ""
    middle_name = ""
    last_name = ""
    current_name = ""
    if 'patient' in first_three_lines.split() and 'named' in first_three_lines.split():
        for token in doc:
            if token.ent_type_ == "PERSON":
                current_name += token.text + " "
            else:
                if current_name.strip():
                    patient_name += current_name.strip() + " "
                    current_name = ""

    # Handle the last name if present
    if current_name.strip():
        patient_name += current_name.strip()
    # Remove duplicate names
    patient_name = ' '.join(list(dict.fromkeys(patient_name.split())))
    print(patient_name)
    name_parts = patient_name.split()

    num_words = len(name_parts)
    if num_words == 2:
        # If the author name has only 2 words, consider them as first and last names
        first_name = name_parts[0]
        last_name = name_parts[1]
    elif num_words == 0:
        first_name = "Unk"
    elif num_words == 1:
        first_name = name_parts[0]
    elif num_words >= 3:
        first_name = name_parts[0]
        middle_name = name_parts[1]
        last_name = " ".join(name_parts[2:])

    print("First name:", first_name)
    print("Middle name:", middle_name)
    print("Last name:", last_name)

    # Initials
    initials = ""
    if first_name == 'Unk':
        initials = 'Unk'
    elif not last_name:
        initials = first_name[0]
    else:
        initials = first_name[0] + last_name[0]
    print("Initials:", initials)

    # OCCUPATION
    occupation = ""
    print("Occupation", occupation)

    # Medical record source type
    medical_record_source_type_keywords = ["GP", "Specialist", "Hospital Record", "Investigation", "gpmrn",
                                           "specialistMrn", "hospitalMrn", "investigation"]
    medical_record_source_type = ""
    print("Medical record source type:", medical_record_source_type)

    # Medical record number
    medical_record_number = ""
    print("Medical Record number:", medical_record_number)

    # Age
    age = ""
    time_unit = ""
    time_unit_=""
    time_units = ["year", "day", "decade", "month", "hour", "weeks"]

    # Regular expression pattern to match age information with hyphen and different time units
    pattern = r'(\d+)\s*-?\s*(' + '|'.join(time_units) + ')'
    age_pattern = re.compile(pattern)
    matches = age_pattern.findall(first_three_lines)
    if matches:
        ages, time_unit_ = int(matches[0][0]), matches[0][1]
        match_index = first_three_lines.find(matches[0][1], first_three_lines.find(matches[0][0]))
        if match_index != -1 and first_three_lines.find("old", match_index) != -1:
            age = ages
            time_unit = time_unit_
    print("Age at time of onset of reaction:", age)

    # Extract units
    if time_unit_:
        time_unit = time_unit_
    else:
        pattern_1 = r'\s*(' + '|'.join(time_units) + ')'
        age_pattern = re.compile(pattern_1, flags=re.IGNORECASE)

        matches = age_pattern.findall(first_three_lines)
        for match in matches:
            if match:
                time_unit = match

    print("Age at time of onset of reaction(units):", time_unit)

    # Date of birth
    date_of_birth = ""
    if "born" in first_three_lines.split(" "):
        dob_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
        matches = dob_pattern.findall(first_three_lines)
        if matches:
            date_of_birth = matches[0]
    print("Date of birth:", date_of_birth)

    # Age group
    age_groups = ['Foetus', 'Neonate', 'Infants', 'Child', 'Adolescent', 'Adults', 'Elderly']

    age_group = ""
    if age:
        if (0 <= age <= 12 and time_unit == time_units[3]) or (1 <= age <= 50 and time_unit == time_units[5]) or (
                time_unit == time_units[4]):
            age_group = age_groups[1]
            print("Age group:", age_groups[1])
        elif (1 <= age <= 3 and time_unit == time_units[0]) or (13 <= age <= 36 and time_unit == time_units[3]):
            print("Age group:", age_groups[2])
            age_group = age_groups[2]
        elif 3 <= age <= 11 and time_unit == time_units[0]:
            print("Age group:", age_groups[3])
            age_group = age_groups[3]
        elif 12 <= age <= 18 and time_unit == time_units[0]:
            print("Age group:", age_groups[4])
            age_group = age_groups[4]
        elif (19 <= age <= 69 and time_unit == time_units[0]) or (3 <= age <= 6 and time_unit == time_units[2]):
            print("Age group:", age_groups[5])
            age_group = age_groups[5]
        elif (age > 69 and time_unit == time_units[0]) or (7 <= age < 10 and time_unit == time_units[2]):
            print("Age group:", age_groups[6])
            age_group = age_groups[6]
        else:
            print("Age group:", age_groups[0])
            age_group = age_groups[0]

    if age_group == age_groups[0]:
        parent_child_foetus_case = "Yes"
    else:
        parent_child_foetus_case = "No"
    # Sex
    patient_gender = ["Male", "Female", "Unknown"]

    sex = ""
    for token in doc:
        if token.text.lower() in ["male", "he", "his", "young man", "gentleman", "man", "boy"]:
            sex = patient_gender[0]
            break
        elif token.text.lower() in ["female", "she", "her", "young woman", "woman", "girl"]:
            sex = patient_gender[1]
            break
        else:
            sex = patient_gender[2]
    print("Sex:", sex)

    if sex == patient_gender[2]:
        initials = "UNK"
    # GROUP OF PATIENT
    ethnic_group = ""
    ethnic = ""
    ethnic_groups = [
        "African American",
        "American Indian or Alaska Native",
        "Asian",
        "Black",
        "Caucasian",
        "Native Hawaiian or Other Pacific",
        "Other",
        "White"
    ]

    groups = [
        "African American",
        "American Indian",
        "Alaska Native",
        "Asian",
        "Black",
        "Caucasian",
        "Native Hawaiian",
        "Other Pacific",
        "Other",
        "White", "white", "african american", "american indian","asian", "alaska mative", "black", "caucasian", "native hawaiian", "other pacific"]
    print("fisrt three lines split", first_three_lines.split(" "))
    for i in groups:
        if i in first_three_lines.split(" "):
            ethnic_group = i
            print("yes ethnic matched")
    if ethnic_group == "African American" or ethnic_group == "african american":
        ethnic = ethnic_groups[0]
    elif ethnic_group == "American Indian" or ethnic_group == "Alaska Native" or ethnic_group == "american indian" or ethnic_group =="alaska mative":
        ethnic = ethnic_groups[1]
    elif ethnic_group == "Asian" or ethnic_group == "asian":
        ethnic = ethnic_groups[2]
    elif ethnic_group == "Black" or ethnic_group == "black":
        ethnic = ethnic_groups[3]
    elif ethnic_group == "Caucasian"or ethnic_group == "caucasian":
        ethnic = ethnic_groups[4]
    elif ethnic_group == "Native Hawaiian" or ethnic_group == "Other Pacific" or ethnic_group == "native hawaiian"or ethnic_group =="other pacific":
        ethnic = ethnic_groups[5]
    elif ethnic_group == "White" or ethnic_group =="white":
        ethnic = ethnic_groups[7]
    print("Ethnic_group:", ethnic)

    # Weight
    weight = ""
    units = " "

    # Regular expression pattern to match weights with various units
    weight_pattern = re.compile(r'\b(\d+(\.\d+)?)\s*(kgs?|grams?|g|Kilo\s*grams?)\b(?!/dL)', re.IGNORECASE)

    # Find all matches in the text
    matches = weight_pattern.findall(first_three_lines)
    print("matches from weight",matches)
    sentence = ""
    # Extract weights and units if matches are found
    for match in matches:
        weight, _, units = match
        match_start = first_three_lines.find(match[0])
        match_end = match_start + len(match[0])
        sentence_start = max(0, first_three_lines.rfind('.', 0, match_start))
        sentence_end = first_three_lines.find('.', match_end)
        sentence = first_three_lines[sentence_start:sentence_end].strip()

    if any(word in sentence.lower() for word in ['weigh']):
        if units in ["g", "grams"]:
            converted_weight = int(weight) / 1000
            weight = converted_weight
        elif units.lower() in ["lbs", "pounds"]:
            # Convert pounds to kilograms (1 lb = 0.453592 kg)
            converted_weight = int(weight) * 0.453592
            weight = converted_weight
        else:
            weight = weight
    print("Weight (kg):", weight)

    # Height
    height = ""
    inches = ""
    height_in_cm = ""
    # Regular expression pattern to match heights in various units
    height_pattern = re.compile(r'\b(\d+)\s*(cm|centimeters|feet|ft)\s*(\d+)?\s*(inches)?\b', re.IGNORECASE)

    # Find all matches in the text
    matches = height_pattern.finditer(first_three_lines)

    # Extract heights and units if matches are found
    for match in matches:
        height, units, inches, _ = match.groups()
        # Find the entire sentence containing the height information
        sentence_start = max(0, first_three_lines.rfind('.', 0, match.start()))
        sentence_end = first_three_lines.find('.', match.end())
        sentence = first_three_lines[sentence_start:sentence_end].strip()

    if any(word in sentence.lower() for word in ['height', 'tall']):
        if units.lower() in ['feet', 'ft']:
            height_in_cm = int(height) * 30.48  # Convert feet to cm
            if inches:
                height_in_cm += int(inches) * 2.54  # Convert inches to cm
            print("Height (cm):", height_in_cm)
        else:
            height_in_cm = height
            print("Height (cm):", height_in_cm)
    else:
        print("Height (cm):", height_in_cm)

    # Opening Female section
    # LMP
    last_menstrual_period = ""
    pregnant = ['Yes', 'No', 'Unknown']

    edd = ""
    pregnant_ = ""
    gestation_period = ""
    gestation_period_units = ""
    pregnant_at_time_of_vaccination = ['Yes', 'No']
    menstrual_period = ['lmp', 'l.m.p', 'last menstrual period']
    estimation_delivery_date = ['edd', 'estimation delivery date']
    if sex == patient_gender[1]:

        for word in menstrual_period:
            if word in first_three_lines.lower():
                sentence_start = max(0, first_three_lines.rfind('.', 0, first_three_lines.lower().find(word)))
                sentence_end = first_three_lines.find('.', first_three_lines.lower().find(word))
                sentence = first_three_lines[sentence_start:sentence_end].strip()

                # Search for a date pattern in the same sentence
                date_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
                date_match = date_pattern.search(sentence)
                if date_match:
                    last_menstrual_period = date_match.group(1)
        print("Last Menstrual period", last_menstrual_period)

        # pregnant or not
        if 'not pregnant' in first_three_lines.lower():
            pregnant_ = pregnant[1]

        elif 'pregnant' in first_three_lines.lower() and "not pregnant" not in first_three_lines:
            pregnant_ = pregnant[0]
        else:
            pregnant_ = pregnant[2]
        print("pregnant:", pregnant_)

        # Pregnant information extraction after confirms
        if pregnant_ == "Yes":

            for word in estimation_delivery_date:
                if word in first_three_lines.lower():
                    sentence_start = max(0, first_three_lines.rfind('.', 0, first_three_lines.lower().find(word)))
                    sentence_end = first_three_lines.find('.', first_three_lines.lower().find(word))
                    sentence = first_three_lines[sentence_start:sentence_end].strip()
                    print(f"EDD Word '{word}' related to estimation delivery date found in the text.")
                    print(f"EDD Sentence: '{sentence}'")

                    date_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
                    date_match = date_pattern.search(sentence)
                    if date_match:
                        edd = date_match.group(1)
                    else:
                        date_pattern = re.compile(r'\b(\w+ \d{1,2}, \d{4})\b')

                        # Search for the date pattern in the text
                        date_match = date_pattern.search(first_three_lines)

                        # Extract and print the date if found
                        if date_match:
                            edd = date_match.group(1)
            print("Estimation delivery date", edd)

            # OUTCOME OF PREGNANCY
            outcome_of_pregnancy = [
                "Congrnital abnormality",
                "Live birth at term",
                "Other medically Significant",
                "Premature delivery",
                "Spontaneous abortion",
                "Still born",
                "Still born Unknown"
            ]

            # Gestation period

            gestation_period_unit = ["Trimester", "Day", "Month", "Week"]

            # Regular expression pattern to match age information with hyphen and different time units
            pattern = r'(\d+)\s*-?\s*(' + '|'.join(gestation_period_unit) + ')'
            gestation_period_pattern = re.compile(pattern)
            matches = gestation_period_pattern.findall(first_three_lines)
            if matches:
                gestation_period, gestation_period_units = int(matches[0][0]), matches[0][1]
            print("Gestation period::", gestation_period)
            print("Gestation period units:", gestation_period_units)

            concomitant_therapy_administered = ['true', 'false']
            breastfeeding = ['true', 'false']

    # ADDRESS EXTRACTION
    found_patient_countries = ""
    city_ = ""
    is_part_of_city = False
    city = ""
    address = ""
    affiliations = first_three_lines.split("\n")
    # List of keywords indicating country information
    country_keywords = ["resides", " is from", "country"]
    # Loop through affiliations and search for country names and cities
    for affiliation in affiliations:
        for keyword in country_keywords:
            if keyword in affiliation:
                country_found = False  # Flag to indicate if a country has been found in this affiliation
                deleted_countries = ['Iran', 'South Korea', 'North Korea', 'Korea', 'Sudan', 'MACAU',
                                     'Republic Of Ireland',
                                     'USA']
                for i in deleted_countries:
                    if i in affiliation:
                        found_patient_countries.append(i)
                        country_found = True
                        break

                for country in pycountry.countries:
                    if country.name in affiliation and not found_patient_countries:
                        found_patient_countries = country.name
                        country_found = True
                        break  # Stop searching for country names in this affiliation
                country_doc = nlp(affiliation)
                for token in country_doc:
                    if token.ent_type_ == "GPE" and token.text:
                        city = token.text

    # If the city string isn't finished at the end
    if city != found_patient_countries:
        city_ = city

    # city
    print("Patient City:", city_)

    # State
    state = " "
    print("Patient state:", state)

    # Pincode
    pincode = " "
    json_file = "postal-codes.json"
    with open(json_file, encoding='utf-8-sig') as file:
        country_regexes = json.load(file)
    pin_codes = []

    # Get the text before the first period in the first split
    desired_text = first_three_lines
    for country_data in country_regexes:
        regex_pattern = country_data["Regex"]
        modified_pattern = r"\b" + re.sub(r'^\^|\$$', '', regex_pattern) + r"\b"

        matches = re.finditer(modified_pattern, desired_text)
        for match in matches:
            # Get the starting and ending positions of the match
            match_start = match.start()
            match_end = match.end()

            # Find the sentence start and end positions
            sentence_start = max(0, desired_text.rfind('.', 0, match_start))
            sentence_end = desired_text.find('.', match_end)

            # Extract the sentence and strip leading/trailing whitespaces
            sentence = desired_text[sentence_start:sentence_end].strip()
            if found_patient_countries and found_patient_countries[0] in sentence:
                pin_codes.append(match.group())

    max_digit_count = 0
    string_with_max_digits = ''

    for string in pin_codes:
        digit_count = sum(c.isdigit() for c in string)  # Count the number of digits in the string
        if digit_count > max_digit_count:
            max_digit_count = digit_count
            pincode = string
    print("Patient Pincode:", pincode)

    # Print the found countries
    print("Patient Country:", found_patient_countries)

    # Phone number
    lines = first_three_lines.split('\n')

    # Variable to store the extracted phone numbers
    phone_number = ""

    # Find the line containing 'Fax' or 'Tel' and extract text after that
    for line in lines:
        if 'Fax' in line or 'Tel' in line or '+' in line or 'Phone' in line:
            # Extract the text after 'Fax' or 'Tel'
            # extracted_text = line.split('Fax:')[-1].strip() if 'Fax' in line else line.split('Tel:')[-1].strip()
            extracted_text = line

            # Extract numbers with the '+' character
            numbers_with_plus = re.findall(r'\+\d[\d -]+', extracted_text)
            numbers_with_plus_in_brackets = re.findall(r'\(\+\d+\)-\d+', line)
            numbers_with_plus_in_brackets_and_space = re.findall(r'\(\+\d+\) \d+', line)
            if numbers_with_plus:
                phone_number = numbers_with_plus
            elif numbers_with_plus_in_brackets:
                phone_number = numbers_with_plus_in_brackets
            elif numbers_with_plus_in_brackets_and_space:
                phone_number = numbers_with_plus_in_brackets_and_space

    print("Patient PhoneNumber", phone_number)

    # Email pattern
    email_address = " "
    email_pattern = r'\b[A-Za-z0-9._%+-]+ ?@ ?[A-Za-z0-9.-]+ ?\.[A-Z|a-z]{2,}\b'
    # Find email addresses in the text
    patient_email = re.findall(email_pattern, first_three_lines)
    if patient_email:
        email_address = patient_email
    print("Patient Email Address:", email_address)

    relevant_medical_history_and_concurrent = ""

    # Medical History
    # Starting date
    start_date = ""
    end_date = ""
    history_keywords = ["medical history", "history", "he had", "she had", "diagnosed", "suffered", "presented", "man who had", "woman who had"]
    start_line = None
    history_keyword = ""
    history_comments = ""
    end_line = -1
    # for num, row in enumerate(lines):
    #     for keyword in history_keywords:
    #         #print("checking")
    #         if keyword in row:
    #             history_keyword = keyword
    #             print(row)
    #
    #             # Find the start and end indices of the relevant portion of the line
    #             start_line = row.find(keyword)
    #
    #             # Accumulate the text from the current line
    #             history_text = row[start_line:]
    #
    #             # Check if there is a full stop in the remaining text
    #             while end_line == -1 and num + 1 < len(lines):
    #                 num += 1
    #                 next_line = lines[num]
    #                 history_text += ' ' + next_line
    #                 end_line = history_text.find('.')
    #
    #             # Extract the text up to the full stop
    #             history_comments += history_text[:end_line + 1] + "\n"
    # print("history comments", history_comments)
    # for i, line in enumerate(lines[:-2]):
    #     for keyword in history_keywords:
    #         if keyword in line:
    #             if i + 1 < len(lines):
    #                 extracted_text = line
    #                 extracted_next_text = lines[i + 1]
    #                 extracted_for_end_date = lines[i + 2]
    #                 pattern = re.compile(
    #                     r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
    #                 )
    #                 match = re.search(pattern, extracted_text)
    #                 if match:
    #                     matched_date = match.group()
    #                     start_date = matched_date
    #                 else:
    #                     match_2 = re.search(pattern, extracted_next_text)
    #                     if match_2:
    #                         matched_date_2 = match_2.group()
    #                         start_date = matched_date_2
    #                 match_end = re.search(pattern, extracted_next_text)
    #                 if match_end:
    #                     matched_end_date = match_end.group()
    #                     if matched_end_date != start_date:
    #                         end_date = matched_end_date
    #                     else:
    #                         match_end_2 = re.search(pattern, extracted_for_end_date)
    #                         if match_end_2:
    #                             matched_date_2 = match_end_2.group()
    #                             end_date = matched_date_2
    #
    # print("Start date:", start_date)
    # print("End date:", end_date)

    # Continuing


    family_history = ["True", "False"]

    # Case of Death
    dead_keywords = ["expired", "died", "dead", "passed away", "demise", "murdered", "lost life"]
    death_comments = ""
    text = ""
    death_text = ""
    death_tet_for_comments =""
    end_text = ""
    dod = ""
    lines = report_to_discussion
    dead_keywords = ["expired", "died", "dead", "passed away", "demised", "murdered", "lost life"]

    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, dead_keywords)) + r')\b', flags=re.IGNORECASE)

    # Search for the keywords in the text
    matches = pattern.findall(text)

    # Output the matches
    if matches:
        for match in matches:
            print(f"Found match: {match}")
            for i, line in enumerate(lines.split('\n')):
                if match in line:
                    print("Yes, keyword found")
                    start_line = line.find(match)
                    text = line[start_line:]

                    next_line_index = i + 1
                    while next_line_index < len(lines.split('\n')):
                        if "." in lines.split('\n')[next_line_index]:
                            print("Yes, '.' is present in the next line")
                            end_line = lines.split('\n')[next_line_index]
                            print(end_line)
                            death_tet_for_comments += text + end_line + "\n"
                            break
                        next_line_index += 1
            death_text += text + "\n"
    else:
        print("************not matched*********")


    # end_line = death_text.find('.')
    # death_comments = death_text[:end_line]
    dod_pattern = re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b')
    matches = dod_pattern.findall(death_text)
    if matches:
        dob = matches[0]
    print("Date of death:", dod)

    # Cause of death
    cause_of_death = []
    death_llt = []
    doc = nlp_1(death_text)
    # for ent in doc.ents:
    #     if ent.label_ == "DISEASE" and ent.text not in dead_keywords:
    #         cause_of_death.append(ent.text)
    #         death_llt.append(ent.text)
    for ent in doc.ents:
        if ent.type == "PROBLEM" and ent.text not in dead_keywords:
            cause_of_death.append(ent.text)
            death_llt.append(ent.text)
    death_llt_set = list(set(death_llt))
    death_llt_string = ','.join(death_llt_set)
    cause_of_death_string = ','.join(cause_of_death)
    print("Cause of death", cause_of_death_string)
    print("LLT", death_llt_string)
    cause_of_death_comments = death_llt
    print("Comments", death_text)
    # AUTOPSY PART
    autopsy_keywords = ["autopsy", "Post-mortem", "necropsy", "examination", "medical examination", "post mortem"]
    autopsy_done = ["true", "false", "UNk", "ASKU"]

    text_after_autopsy = " "
    autopsy_text = ""
    autopsy = ""
    lines = death_text.split("\n")
    if death_text:
        for i, line in enumerate(lines):
            for keyword in autopsy_keywords:
                if line in keyword:
                    autopsy = autopsy_done[0]
                    start_line = line.find(keyword)
                    text_after_autopsy = line[start_line:]

                    # end_line = death_text.find('.')
                    # death_comments = death_text[:end_line]
                elif keyword in line and "no" in line or "not" in line:
                    autopsy = autopsy_done[1]
                else:
                    autopsy = autopsy_done[2]


    autopsy_text += text_after_autopsy + "\n"
    print("Autopsy:", autopsy)
    autopsy_cause_of_death = []
    autopsy_llt = []
    doc = nlp_1(autopsy_text)
    # for ent in doc.ents:
    #     if ent.label_ == "DISEASE" and ent.text not in dead_keywords:
    #         autopsy_cause_of_death.append(ent.text)
    #         autopsy_llt.append(ent.text)
    for ent in doc.ents:
        if ent.type == "PROBLEM" and ent.text not in dead_keywords:
            autopsy_cause_of_death.append(ent.text)
            autopsy_llt.append(ent.text)
    if "COVID" in autopsy_text:
        autopsy_cause_of_death.append("COVID-19")
        autopsy_llt.append("COVID-19")

    autopsy_llt_set = list(set(autopsy_llt))
    autopsy_llt_string = ', '.join(autopsy_llt_set)
    autopsy_cause_of_death_string = ', '.join(autopsy_cause_of_death)
    print("Cause of death", autopsy_cause_of_death_string)
    print("LLT", autopsy_llt_string)
    print("Autopsy Comments", autopsy_text)

    # Drug details
    # med7 = spacy.load("en_core_med7_lg")



    # medical llt

    llt_medical_1 = []
    new_lines_for_text_before_medicine=""
    period_before_negative_line = ""
    period_after_negative_line= ""
    print("text before med is#####", text_before_medicine)
    # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None, use_gpu=False)


    negative_line_keywords = ["absent", "no", "not", "normal", "without", "not significant", "excluded"]

    articles = ['a', 'an', 'the', 'these', 'those', 'were']
    period_before_negative_line = ""
    new_lines_for_text_before_medicine = ""
    for line in text_before_medicine.split('.'):
        contains_negative_keyword = any(negative in line.lower() for negative in negative_line_keywords)

        if not contains_negative_keyword:
            # Check for articles and exclude lines that contain them
            doc = nlp(line)

            # Filter out common words
            filtered_tokens = [token.text for token in doc if token.text.lower() not in articles]

            # Join the filtered tokens to form a new line
            new_line = ' '.join(filtered_tokens)

            new_lines_for_text_before_medicine += new_line + '\n'

    print("new_line++++", new_lines_for_text_before_medicine)
    # Process the text using spaCy
    doc_1 = nlp_1(new_lines_for_text_before_medicine)

    # for ent in doc.ents:
    #     if ent.label_ == "DISEASE" and len(ent.text) > 3:
    #         llt_medical.append(ent.text)
    for ent in doc_1.entities:
        if ent.type == "PROBLEM" and len(ent.text) > 3:
            llt_medical_1.append(ent.text)
    print("Indication LLT:", llt_medical_1)
    print("Indication Comment:", text_before_medicine)

    filtered_llt = list(set(llt_medical_1))
    llt_medical=[]
    #
    #changed here to new code, validation is left############################

    df = pd.read_csv("LLT_Details_26_1.csv")
    print(df.columns)
    for llt in filtered_llt:
        print(llt)
        result = df.loc[df['LLT_NAME'].str.lower().str.contains(llt.lower()), 'LLT_NAME'].values

        if len(result) > 0:
            llt_medical.append(llt)
            print(llt)

    llt_medical_string = ', '.join(filtered_llt)

    # using stanza
    # stanza.download('en', package='mimic', processors={'ner': 'i2b2'})
    # nlp_3 = stanza.Pipeline('en', package='mimic', processors={'ner': 'i2b2'})
    # annotate clinical text
    # doc = nlp_3(text_before_medicine)
    # # print out all entities
    # for ent in doc.entities:
    #    if ent.type == "PROBLEM":
    #        print("from stanza", ent.text)
    period_before_llt_index = -1
    period_after_llt_index = -1

    for llt in llt_medical:
        llt_start_index = text_before_medicine.find(llt)

        if llt_start_index != -1:
            print("1 yes", period_after_llt_index)
            # Find the period before llt
            period_before_llt_index = text_before_medicine.rfind(".", 0, llt_start_index)

        if period_before_llt_index != -1:
            print("2 yes", period_before_llt_index)
            # Find the first period after llt
            period_after_llt_index = text_before_medicine.find('.', llt_start_index)

            # Check if '.' was found
            if period_after_llt_index != -1:
                print("3 yes", period_after_llt_index)
                # Extract the substring between period_before_llt_index and period_after_llt_index
                history_comments = text_before_medicine[period_before_llt_index:period_after_llt_index]

        # start and end date
        pattern = re.compile(
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
        )
        match = re.search(pattern, history_comments)
        if match:
            matched_date = match.group()
            start_date = matched_date
        match_end = re.search(pattern, history_comments)
        if match_end:
            matched_end_date = match_end.group()
            if matched_end_date != start_date:
                end_date = matched_end_date
        # continuing
        continuing_list = ['true', 'false', 'null']
        if end_date:
            continuing = continuing_list[1]
        elif "continu" in history_comments.lower():
            continuing = continuing_list[0]
        else:
            continuing = continuing_list[2]


        medical_history={
            "disease_surgical_procedure": "",
            "meddra_version": "",
            "start_date": start_date,
            "end_date": end_date,
            "continuing": continuing,
            "llt": llt,
            "comments": history_comments,
            "family_history": ""
        }
        all_medical_history.append(medical_history)
        print("Comments for history llt $$$$$:", history_comments)

    # Process the text using the loaded model
    # doc = nlp("there are people with imbalanced theme. septic-embolic brain lesions were observed")
    # # print out all entities
    # for ent in doc.entities:
    #     if ent.type == "PROBLEM":
    #         print("from stanza_2", ent.text)
    drugs = set()
    # for ent in doc.entities:
    #    if ent.type == "TREATMENT":
    #        print("from stanza drugs", ent.text)
    #        drugs.add(ent.text)
    # print("drugs set  is", drugs)
    # Access entities in the processed document
    doc_1=nlp_1(text_before_medicine)
    print("entered for drugs//////")
    for ent in doc_1.ents:
        if ent.type == "TREATMENT" and ent.text != "RVD" and ent.text != drug_found and ent.text != "DOI" and len(ent.text)>3:
            drugs.add(ent.text)
            print("drugs are:", ent.text)
    for line in text_before_medicine.split('\n'):
        if 'rituximab' in line:
            drugs.add('rituximab')

    drugs_to_remove = set()

    negative_drug_words = {'DOI', 'RVD', 'https', 'mcg/ml', 'TCPDF', 'CD138', 'eosin'}
    for drug in products['product_name']:
        for past_drug in drugs:
            if drug.lower() in past_drug or any(
                    negative_word in past_drug for negative_word in negative_drug_words):
                drugs_to_remove.add(past_drug)

    # Remove the drugs after the iteration
    for drug_to_remove in drugs_to_remove:
        drugs.remove(drug_to_remove)
    drugs_list = list(set(drugs))
    drugs_string = ', '.join(drugs_list)
    print("drugs list is", drugs_string)

    past_drug_reaction_text = ""
    past_drug_indication_text = ""

    # iterating through drug names
    for i, past_drug in enumerate(drugs_list):
        drug_start_index = text_before_medicine.find(past_drug)
        next_drug_index = i + 1
        period_before_past_drug_index = ""
        # Check if llt is found
        if drug_start_index != -1:
            past_drug_indication_text=text_before_medicine[:drug_start_index]
            print("********amul past drug is***********", past_drug_indication_text)
            # Find the period before llt
            period_after_past_drug_index = text_before_medicine.find('.', drug_start_index)

            # Check if '.' was found
            if period_after_past_drug_index != -1:
                print(f"The period after drug_start_index is at position {period_after_past_drug_index}")
                # Extract the substring after drug_start_index until the period
                past_drug_reaction_text = text_before_medicine[drug_start_index:period_after_past_drug_index]
        indication_text = past_drug_indication_text

        # for i, line in enumerate(lines):
        #     for keyword in indication_keywords:
        #         if keyword in line:
        #             start_line = line.find(keyword)
        #             text_for_indication = line[start_line:]
        #
        #             # end_line = death_text.find('.')
        #             # death_comments = death_text[:end_line]
        # indication_text += text_for_indication + "\n"
        llt_indicators = []
        # nlp = stanza.Pipeline('en', package='CRAFT', processors={'ner': 'bc5cdr'}, download_method=None, use_gpu=False)

        period_before_negative_line = ""
        new_lines_for_indication_text = ""
        for line in indication_text.split('.'):
            contains_negative_keyword = any(negative in line.lower() for negative in negative_line_keywords)

            if not contains_negative_keyword:
                # Check for articles and exclude lines that contain them
                doc = nlp(line)

                # Filter out common words
                filtered_tokens = [token.text for token in doc if token.text.lower() not in articles]

                # Join the filtered tokens to form a new line
                new_line = ' '.join(filtered_tokens)

                new_lines_for_indication_text += new_line + '\n'

        print("new_line++++", new_lines_for_indication_text)
        doc = nlp_1(new_lines_for_indication_text)

        for ent in doc.ents:
            if ent.type == "PROBLEM":
                llt_indicators.append(ent.text)
        llt_indicator_set = list(set(llt_indicators))


        new_llt_indicators=[]
        for llt in llt_indicator_set:
            result = df.loc[df['LLT_NAME'].str.lower().str.contains(llt.lower()), 'LLT_NAME'].values
            #result = df.loc[df['LLT_NAME'].str.lower().str.extract(f'({llt.lower()})', expand=False).notnull(), 'LLT_NAME'].values.flatten()
            if len(result) > 0:
                new_llt_indicators.append(llt)

        llt_indicators_string = ','.join(new_llt_indicators)



        # start and end of drugs
        start_date_drug = ""
        end_date_drug = ""
        pattern = re.compile(
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
        )
        match = re.search(pattern, indication_text)
        if match:
            matched_date = match.group()
            start_date_drug = matched_date
        match_end = re.search(pattern, indication_text)
        if match_end:
            matched_end_date = match_end.group()
            if matched_end_date != start_date:
                end_date_drug = matched_end_date

        # Reaction after drug
        llt_reactions = []
        new_llt_reactions = []
        new_lines_for_reaction_text=""
        for line in past_drug_reaction_text.split('.'):
            contains_negative_keyword = any(negative in line.lower() for negative in negative_line_keywords)

            if not contains_negative_keyword:
                # Check for articles and exclude lines that contain them
                doc = nlp(line)

                # Filter out common words
                filtered_tokens = [token.text for token in doc if token.text.lower() not in articles]

                # Join the filtered tokens to form a new line
                new_line = ' '.join(filtered_tokens)

                new_lines_for_reaction_text += new_line + '\n'

        doc = nlp_1(new_lines_for_reaction_text)
        for ent in doc.ents:
            if ent.type == "PROBLEM":
                llt_reactions.append(ent.text)
        llt_reactions_set = list(set(llt_reactions))
        for llt in llt_reactions_set:
            result = df.loc[df['LLT_NAME'].str.lower().str.contains(llt.lower()), 'LLT_NAME'].values
            # result = df.loc[
            #     df['LLT_NAME'].str.lower().str.extract(f'({llt.lower()})', expand=False).notnull(), 'LLT_NAME'].values
            if len(result) > 0:
                new_llt_reactions.append(llt)

        llt_reactions_string = ', '.join(new_llt_reactions)

        comment_reactions = past_drug_reaction_text


        print("Every drug name", past_drug)
        print("### comments are ###", past_drug_reaction_text)
        print("Indication LLT:", llt_indicators)
        print("Reaction LLT:", llt_reactions)
        print("start date drug", start_date_drug)
        print("end date drug", end_date_drug)

        drug_information = {
            "name_of_drug": past_drug,
            "active_or_molecules": past_drug,
            "start_date": start_date_drug,
            "end_date": end_date_drug,
            "llt_indication": llt_indicators_string,
            "llt_indication_medracode": "",
            "llt_indication_version": "",
            "llt_reaction": llt_reactions_string,
            "llt_reaction_medracode": "",
            "llt_reaction_version": "",
            "comments": comment_reactions,
            "condition_type": "",
            "verbatim": ""
        }

        all_drug_information.append(drug_information)
    # past_drug_indication_text = ""
    # past_drug_reaction_text = ""
    # drug_previous_lines=[]
    # for line_number, line in enumerate(text_before_medicine.split('\n')):
    #     for past_drug in drugs_list:
    #         if past_drug.lower() in line.lower():
    #             past_drug_found = past_drug.lower()
    #             line_index = line.lower().find(past_drug.lower())
    #             text_line = line[:line_index + len(past_drug)]
    #
    #             # Combine the current line and the previous lines before the medicine
    #             past_drug_indication_text += "\n".join(drug_previous_lines) + "\n" + text_line + "\n"
    #
    #             # Store the lines after the medicine is found
    #             past_drug_reaction_text += "\n".join(text_before_medicine.split('\n')[line_number + 1:])
    #
    #             # Clear previous_lines for the next iteration
    #             drug_previous_lines = []
    #
    #             # Stop searching for other drugs in the same line once one is found
    #             break
    #
    #     # Store the current line in previous_lines
    #     previous_lines.append(line)




    # Indication
    indication_keywords = ["noticed", "observed", "experienced", "suffered", "reported", "developed", "showed",
                           "encountered", "treat"]
    text_for_indication = ""
    #lines = text_before_medicine.split('\n')[-5:]


    patient = {
        "patient_information": {
            "parent_child_foetus_case": parent_child_foetus_case,
            "protect_confidentiality": protect_confidentiality,
            "title": title,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "initials": initials,
            "occupation": occupation,
            "medical_record_source_type": medical_record_source_type,
            "medical_record_number": medical_record_number,
            "age_at_time_of_onset_of_reaction": age,
            "age_at_time_of_onset_of_reaction_units": time_unit,
            "date_of_birth": date_of_birth,
            "age_group": age_group,
            "sex": sex,
            "ethnic_group": ethnic,
            "weight": weight,
            "height": height_in_cm,
            "last_menstrual_period": last_menstrual_period,
            "pregnant": pregnant_,
            "expected_delivery_date": edd,
            "outcome_of_pregnancy": "",
            "gestation_period_when_reaction_was_observed_in_foetus": gestation_period,
            "gestation_period_units": gestation_period_units,
            "concomitant_therapy_administered": "",
            "breastfeeding": "",
            "pregnant_at_time_of_vaccination": "",
            "military_status": "",
            "address_1": address,
            "address_2": "",
            "city": city_,
            "state_or_province": "",
            "pincode": pincode,
            "country": found_patient_countries,
            "phone_number": phone_number,
            "email_address": email_address,
            "relevant_medical_history_and_concurrent_conditions": relevant_medical_history_and_concurrent
        },
        "medical_history": all_medical_history,
        "past_drug_history": all_drug_information,
        "case_death": {
            "date_of_death": dod,
            "cause_of_death": cause_of_death_string,
            "llt_case_of_death": death_llt_string,
            "medra_code": "",
            "medra_version": "",
            "comment": death_tet_for_comments,
            "was_autopsy_done": autopsy,
            "autopsy_cause_of_death": autopsy_cause_of_death_string,
            "llt_autopsy": autopsy_llt_string,
            "auto_spy_medra_code": "",
            "auto_spy_medra_version": ""

        }
    }
    return patient

# patient_response = get_patient_text(source_text=all_text,en_core=nlp, bcd5r=nlp_1)
# print(patient_response)