import re
import pandas as pd
import pycountry
import json
from metapub import PubMedFetcher, config

def get_country(title, weekly_text_1, en_core):
    title_of_page = title
    print("title_of_page", title)
    weekly_text = weekly_text_1
    nlp = en_core
    extracted_text = ""
    weekly_doc = nlp(weekly_text)

    author_name = ""
    found_countries = ""
    found_cities = []
    text_up_to_doi=""

    # getting title from literature

    if title_of_page:


        if all(word in weekly_doc.text for word in title_of_page.split()[:3]):
            weekly_split = weekly_text.split('\n')

            print("weekly spli is", weekly_split)
            print(title_of_page.split())
            for i, line in enumerate(weekly_split):
                if (
                        title_of_page.split()[0] in line
                        and
                        title_of_page.split()[1] in line
                        and
                        title_of_page.split()[3] in line
                        and
                        title_of_page.split()[4] in line
                ):
                    print("yes we got into title")
                    line_index = i
                    print("line_index", i)
                    extracted_text = '\n'.join(weekly_split[line_index + 1:])
                    print("extracted_text", extracted_text)

                    break

            text_lines = extracted_text.split('\n')
            print("text_lines", text_lines)
            author_line = None
            text_up_to_affiliations = ""

            for line in text_lines:
                if "Affiliations" in line:
                    print("yes affiliations")
                    break
                text_up_to_affiliations += line

            affiliations = text_up_to_affiliations.split("\n")
            print("text_up to affiliatins", affiliations)
            match = re.search(r'Authors([\s\S]*?)\b1\b', text_up_to_affiliations)
            if match:
                print("yes matched authors")
                author_name_before_1 = match.group(1).strip()
                if ',' in author_name_before_1:
                    print("if block")
                    first_author_name = author_name_before_1.split(',')[1]
                    author_name = re.sub(r'\d', '', first_author_name)
                    print(author_name)
                else:
                    print("else block")
                    first_author_name = author_name_before_1
                    author_name = re.sub(r'\d', '', first_author_name)


            # country

            text_up_to_doi = ""
            is_part_of_city = False
            city = ""

            if author_name.lower() in weekly_doc.text.lower():
                print('author_name', author_name.lower())
                #print('11')
                # Find the index of the specific word
                word_index = weekly_doc.text.find(author_name)

                # Extract text after the specific word
                extracted_text = weekly_doc.text[word_index + len(author_name):]
                # Iterate through the lines
                for line in extracted_text.split("\n"):
                    # print('line is', line)
                    #print('12')
                    if "DOI:" in line or "doi" in line:
                        break  # Stop when the line containing "DOI:" is found
                    text_up_to_doi += line
                    # print("text upto doi",text_up_to_doi)
                affiliations = text_up_to_doi.split("\n")
                # Loop through affiliations and search for country names and cities
                for affiliation in affiliations:
                    country_found = False  # Flag to indicate if a country has been found in this affiliation
                    #'MACAU' is deleted
                    deleted_countries = ['Iran', 'South Korea', 'North Korea', 'Korea', 'Sudan',
                                         'Republic Of Ireland',
                                         'USA']
                    for i in deleted_countries:
                        if i in affiliation:
                            found_countries = i
                            country_found = True
                            break

                    for country in pycountry.countries:
                        if country.name in affiliation and not found_countries:
                            found_countries = country.name
                            country_found = True
                            break  # Stop searching for country names in this affiliation
                    country_doc = nlp(affiliation)
                    for token in country_doc:
                        if token.ent_type_ == "GPE" and token.text:
                            if not is_part_of_city:
                                is_part_of_city = True
                                city = token.text
                            else:
                                city += " " + token.text
                        else:
                            if is_part_of_city:
                                found_cities.append(city)
                                is_part_of_city = False
                                city = ""
                countries = " "
                # If the city string isn't finished at the end
                if is_part_of_city != found_countries:
                    found_cities.append(city)
                print("found_countries", found_countries)

            df = pd.read_excel("iso_country_codes.xlsx")

            # Continue with the rest of your code
            if not found_countries:
                print("yes")
                iso_codes = pd.read_excel("iso_country_codes.xlsx")

                if "Affiliation" in text_up_to_doi:
                    affiliation_text = text_up_to_doi.split('Affiliation')[1]
                else:
                    affiliation_text = text_up_to_doi.split('Affiliations')[0]

                department_start_index = affiliation_text.find("ï‚· 1")
                department_end_index = affiliation_text.find(". ï‚· 2")
                department_text = affiliation_text[department_start_index + len('ï‚· 1'):department_end_index]
                print(department_text)
                for index, row in df.iterrows():
                    for word in department_text.split(","):
                        if str(row['Alpha-3 code']).strip().lower() == word.strip().lower():
                            found_countries = word
                        if str(row['Alpha-2 code']).strip().lower() == word.strip().lower():
                            found_countries = word

    return found_countries
