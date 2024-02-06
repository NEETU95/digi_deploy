import requests
from PyPDF2 import PdfReader

from general_reporter import get_general_reporter
from patient_tab import get_patient_text
from parent import get_parent_text
from events_tab import get_events_tab
import spacy
import pysftp
import os
import shutil
import re
from for_country import get_country
from receipt_file import get_receipt
import fitz
import json
import stanza
from stanza.pipeline.core import DownloadMethod


from metapub import PubMedFetcher


# Create a FastAPI instance

# C:\Users\kathiaja\Downloads\Pvtest-main\Pvtest-main\main.py

def pdf_extraction(pdf_info):
    print("*******NLP API CALLING STARTED*********")
    # data_event = json.loads(event['body'])
    # pdf_info = str(data_event['pdf_info'])
    # shutil.copy2('*', '/tmp')

    destination_directory = 'random_temp'
    os.chdir('tmp')
    if os.path.exists(destination_directory):
        shutil.rmtree('random_temp', ignore_errors=True)
    os.makedirs(destination_directory)
    print('dir created')

    # os.makedirs('random_temp', exist_ok=True)  ### changing directory
    os.chdir('random_temp')
    try:
        shutil.copy2('../../product_names.xlsx', '.')
    except shutil.SameFileError:
        pass
    try:
        shutil.copy2('../../medical_event_terms.xlsx', '.')
    except shutil.SameFileError:
        pass
    try:
        shutil.copy2('../../LLT_Details_26_1.csv', '.')
    except shutil.SameFileError:
        pass
    try:
        shutil.copy2('../../iso_country_codes.xlsx', '.')
    except shutil.SameFileError:
        pass
    try:
        shutil.copy2('../../postal-codes.json', '.')
    except shutil.SameFileError:
        pass
    # try:
    #     shutil.copytree('../../custom_ner_model_with_disease', '.')
    # except FileExistsError:
    #     # Handle if the destination directory already exists
    #     pass
    #
    # try:
    #     shutil.copytree('../../custom_ner_model_with_disease_1', '.')
    # except FileExistsError:
    #     # Handle if the destination directory already exists
    #     pass
    success = True
    message = ""
    exception_values = True
    try:
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            # ftp = pysftp.Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969',cnopts=cnopts)
            ftp = pysftp.Connection('demo1.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969',
                                    cnopts=cnopts)
            print("****STARTED SFTP ******")
            with ftp.cd('/upload/pvtestusers/'):
                files = ftp.listdir()
                # print('files : ', files)
                print('pdf_info from code', pdf_info)
                matched_files = list(filter(lambda file: pdf_info in file, files))
                if matched_files:

                    for file in matched_files:
                        ftp.get(file)
                        if 'Weekly' in file:
                            weekly_reader_1 = file
                            print("weekly file", weekly_reader_1)
                        else:
                            source_document = file
                            print("source document", source_document)
                # for file in files:
                #     if pdf_info in file:
                #         print("yes pdf_info")
                #         ftp.get(file)
                #         print('yes downloaded both files')
                #         if 'Weekly' in file:
                #             weekly_reader_1 = file
                #         else:
                #             source_document = file


        except Exception as e:
            # print(f"Exception occurred: {str(e)}")
            success = False
            message = str(e)
            weekly_reader_1 = ""
            source_document = ""
            raise Exception(f"Exception occurred: {str(e)}")

        weekly_reader = PdfReader(weekly_reader_1)
        source_file_reader = PdfReader(source_document)
        # weekly_reader = PdfReader('Weekly literature hits PDF.pdf')
        weekly_reader_num_pages = len(weekly_reader.pages)
        print("222222222222222")

        source_file_num_pages = len(source_file_reader.pages)
        weekly_text_1 = ""
        all_text = ""
        nlp = spacy.load("en_core_web_sm")
        try:
            #stanza.download('en', package='mimic', processors={'ner': 'i2b2'})
            nlp_1=stanza.Pipeline('en', package='mimic', processors={'ner': 'i2b2'})
            print("loaded model")
            # nlp_1 = spacy.load("en_ner_bc5cdr_md")
        except Exception:
            success = False
            message = "Not loaded bcd5r model"
            raise Exception("BCD5R model is not loaded")
        # Loop through all pages and extract text
        first_page = source_file_reader.pages[0]
        print("86")
        first_page_text = first_page.extract_text()
        print(first_page_text)
        # for page_num in range(source_file_num_pages):
        #     page = source_file_reader.pages[page_num]
        #
        #     text = page.extract_text()
        #     if "References" in text or "Bibliography" in text:
        #         references_found = True
        #         break
        #     all_text += text
        print("opening_fitz----")
        print('source_document : ', source_document)
        doc = fitz.open(source_document)  # open a document

        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            all_text += text
            print(f"Page {page_num + 1}:\n{text}\n")

        for page_num in range(weekly_reader_num_pages):
            page = weekly_reader.pages[page_num]
            text = page.extract_text()
            weekly_text_1 += text
        weekly_text = re.sub(r'\s*-\s*', '-', weekly_text_1)
        meta = source_file_reader.metadata
        title_of_page = ""
        # print("title_of_page", meta.title)
        doi = ""
        doi_found = False
        doi_raw = ""
        json_response_from_api = {}
        try:
            if not title_of_page or len(title_of_page.split()) < 2:
                print("checking in first block")
                text_up_to_doi_for_author = ""
                # Iterate through the lines
                for i, line in enumerate(all_text.split("\n")):
                    if "DOI:" in line or "doi:" in line or "DOI:" in line:
                        print("doi is in line", line)
                        if i + 1 < len(all_text.split('\n')):
                            text_up_to_doi_for_author = line
                            # print("text upto doi author", text_up_to_doi_for_author)
                            affiliations = text_up_to_doi_for_author.split("\n")
                            lowercase_text_doi_for_author = text_up_to_doi_for_author.lower()
                            index_doi = lowercase_text_doi_for_author.find('doi:')
                            doi_raw = text_up_to_doi_for_author[index_doi + len('doi:'):].strip()
                            doi_1 = re.sub(r'[^\x00-\x7F]+', '', doi_raw)
                            doi_pattern = re.compile(r'\b10\.\S+\b')
                            matches = doi_pattern.findall(doi_1)
                            if matches:
                                doi = matches[0]
                                doi_found = True
                            print("doi_found", doi_found)
                            print("doi", doi)
                            break
                    else:
                        https_index = all_text.find("http")

                        # If "https" is found, proceed to extract DOI
                        if https_index != -1:
                            print("into https index")
                            # Extract the substring starting from "https"
                            # Extract the substring starting from "https"
                            substring = all_text[https_index:]

                            # urls = re.findall(
                            #     r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                            #     substring)
                            # Define the pattern for matching DOI URLs
                            doi_pattern = re.compile(r'https?:\s*//doi\.org/[^\s]+')

                            # Find all matches in the text
                            matches = doi_pattern.findall(all_text)

                            # Print the matches
                            for match in matches:
                                print("Found DOI URL:", match)

                            # Check if any URLs were found
                            if matches:
                                print("yes", matches)
                                # Extract the text before the URL
                                url_parts = matches[0].split('/')
                                doi_number = '/'.join(url_parts[3:])
                                doi = doi_number
                                print(doi_number)
                                break

                        doi_found = True
                        print("doi_found", doi_found)
                        print("doi", doi)

                if not doi:
                    for i, line in enumerate(all_text.split("\n")):
                        if "DOI:" in line or "doi:" in line:
                            print("yupp")
                            if i + 1 < len(all_text.split('\n')):

                                next_line = all_text.split('\n')[i + 1]
                                print(f"Next line {i + 2}: {next_line}")
                                text_up_to_doi_for_author = line + ' ' + next_line
                                # print("text upto doi author", text_up_to_doi_for_author)
                                affiliations = text_up_to_doi_for_author.split("\n")
                                lowercase_text_doi_for_author = text_up_to_doi_for_author.lower()
                                index_doi = lowercase_text_doi_for_author.find('doi:')
                                doi_raw = text_up_to_doi_for_author[index_doi + len('doi:'):].strip()
                                print("doi_raw is", doi_raw)
                                doi_1 = re.sub(r'[^\x00-\x7F]+', '', doi_raw)
                                doi_pattern = re.compile(r'\b10\.\S+\b')
                                matches = doi_pattern.findall(doi_1)
                                if matches:
                                    doi = matches[0]
                                print("doi", doi)
                                break
                if doi:
                    fetch = PubMedFetcher()
                    print(fetch)
                    print("again", doi)

                    pmid = fetch.pmids_for_query(doi)
                    article = fetch.article_by_pmid(pmid)
                    title_of_page = article.title
                    # ... (other attribute or method access)
                    print("title from pubmed", title_of_page)

                    # print("article is", article)
                    author = article.authors[0]
                    digital_object_identifier = doi
                    literature_reference = article.citation
                    vol = article.volume
                    year = article.year
                    journal = article.journal
                    page = article.pages
                    if page and not any(char.isalpha() for char in page):
                        pages = page

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            success = False
            message = "Title is not found"
            # print("success", success)
            # print("message", message)
            raise Exception(f"Exception occurred: {str(e)}")

        country_verify = ""
        latest_receipt_date = ""
        try:
            # print("checking in 2nd blcok")
            latest_receipt_date = get_receipt(en_core=nlp, weekly_text_1=weekly_text)
            if not latest_receipt_date:
                success = False
                message = "Latest Receipt date is not found"
                raise Exception("latest receipt date is not found")

        except Exception as e:
            # print(f"Exception occurred: {str(e)}")
            success = False
            message = "Latest Receipt date is not found"
            raise Exception("Latest Receipt date is not found")

        try:
            # print("checking in 3rd block")
            country_verify = get_country(title=title_of_page, weekly_text_1=weekly_text, en_core=nlp)
            # print("country is", country_verify)
            if not country_verify:
                success = False
                message = "country is not found"
                raise Exception("country not found")

        except Exception as e:
            # print(f"Exception occurred: {str(e)}")
            success = False
            message = "country is not found"
            # print("success", success)
            # print("message", message)
            raise Exception("country is not found")

        general_extraction = {}
        reporter_extraction = {}
        patient_extraction = {}
        parent_extraction = {}
        try:
            if title_of_page is not None and country_verify is not None and latest_receipt_date is not None:
                general_extraction, reporter_extraction = get_general_reporter(
                    source_text=all_text,
                    weekly_text_1=weekly_text,
                    en_core=nlp,
                    meta_data=meta,
                    first_page=first_page_text
                )
        except Exception as e:
            # print(f"Exception occurred: {str(e)}")
            success = False
            message = f"Exception occurred from general_reporter: {str(e)}"
            # print("success", success)
            # print("message", message)
            raise Exception(f"Exception occurred from general_reporter: {str(e)}")

        try:
            patient_extraction = get_patient_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)
        except Exception as e:
            # print(f"Exception occurred from patient_tab: {str(e)}")
            success = False
            message = f"Exception occurred from patient_tab: {str(e)}"
            # print("success", success)
            # print("message", message)
            raise Exception(f"Exception occurred from patient_tab: {str(e)}")

        try:
            parent_extraction = get_parent_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)
        except Exception as e:
            # print(f"Exception occurred from parent_tab: {str(e)}")
            success = False
            message = f"Exception occurred from parent_tab: {str(e)}"
            # print("success",success)
            # print("message", message)
            raise Exception(f"Exception occurred from parent_tab: {str(e)}")
        try:
            events_extraction = get_events_tab(source_text=all_text, country=country_verify, bcd5r=nlp_1)
        except Exception as e:
            print(f"Exception occurred from events_tab exception: {str(e)}")
            success = False
            message = f"Exception occurred from events_tab: {str(e)}"
            # print("success", success)
            # print("message", message)
            raise Exception(f"Exception occurred from events_tab: {str(e)}")

        # except HTTPException as e:
        #     print(f"Exception occurred from events_tab HTTP exception: {str(e)}")
        #     success = False
        #     message = f"Exception occurred from events_tab: {str(e)}"
        #     #print("success", success)
        #     #print("message", message)
        #     raise Exception(f"Exception occurred from events_tab: {str(e)}")

        print("success above", success)

        try:
            if success == True:
                exception_values = False
                print("entered into success")
                message = "Extracted successfully from NLP model."
                response_for_integration = {
                    "success": True,
                    "message": "Extracted successfully",
                    "first_file_name": weekly_reader_1,
                    "second_file_name": source_document,
                    "general_information": general_extraction,
                    "reporter": reporter_extraction,
                    "patient": patient_extraction,
                    "parent": parent_extraction,
                    "reaction_event": events_extraction
                }
                # json_response_from_api = response.json()
                print("Aws response", response_for_integration)
                # print("*" * 50)

                os.chdir('..')
                shutil.rmtree('random_temp', ignore_errors=True)
                os.chdir('..')
                print("###### Create Case AI API calling started ########")
                url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
                #url_1 = " http://192.168.4.174:8090/SafetyDB/createCaseAI"

                response = requests.post(url, json=response_for_integration)

                if response:
                    response_from_my_api = {
                        "success": success,
                        "message": "saved successfully into database",
                        "first_file_name": weekly_reader_1,
                        "second_file_name": source_document
                    }
                    print("###### Create Case AI API calling Ended ########", response)
                else:
                    response_from_my_api = {
                        "success": success,
                        "message": message,
                        "first_file_name": weekly_reader_1,
                        "second_file_name": source_document
                    }

                # print("response after hitting create case ai url", response)

                return response_from_my_api
            elif success == False:
                exception_values = False
                print("from else", success)
                message = message
                response = {
                    "success": success,
                    "message": message,
                    "first_file_name": weekly_reader_1,
                    "second_file_name": source_document
                }
                # print(response)
                print("###### Create Case AI API calling started from success=false########")
                url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
                #url_1 ="http://192.168.4.174:8090/SafetyDB/createCaseAI"

                # print("=--------------------------------------------------------------------------------------------------------")

                response_from_api = requests.post(url, json=response)
                # print("*" * 50)
                # # print(response_from_api.text)
                # json_response_from_api = response_from_api.json()
                os.chdir('..')
                shutil.rmtree('random_temp', ignore_errors=True)
                os.chdir('..')

                return response
        except Exception as e:
            success = False
            message = str(e)
            raise Exception(f"Exception occurred after extraction of details: {str(e)}")

        print("****** NLP API END ******")


    except Exception as e:
        print("error : ", e)
        response = {
            "success": False,
            "message": message,
            "first_file_name": weekly_reader_1,
            "second_file_name": source_document
        }

        if exception_values == True:
            print("Exception block executed with exception_values True", e)

            # print(response)

            url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
            #url_1 = " http://192.168.4.174:8090/SafetyDB/createCaseAI"



            # print("=--------------------------------------------------------------------------------------------------------")
            print("###### Create Case AI API calling started in exception block ########")
            response_from_api = requests.post(url, json=response)
            # print("*" * 50)
            # print("RESPONSE FROM CREATE CASE",response_from_api.text)
            # json_response_from_api = response_from_api.json()
            if response_from_api:
                print("###### Create Case AI API calling Ended from exception block ########", response_from_api)
            os.chdir('..')

            shutil.rmtree('random_temp', ignore_errors=True)

            os.chdir('..')

            return response
        else:
            print("Exception values False executed")
            return response


