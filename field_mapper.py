# field_mapping.py
"""
Maps between database/form fields and print layout field names
"""

# Map from your form/database fields to print_layout field names
FORM_TO_PRINT_MAPPING = {
    # Header fields
    "SrNo": "serial_no",
    "RegNo": "reg_no", 
    "MasjidName": "masjid_name",
    
    # Date/Time fields
    "HijriDate": "hijri_date",
    "EnglishDate": "eng_date",
    "Time": "nikah_time",
    "PlaceOfNikah": "place_of_nikah",
    
    # Groom fields
    "Bridegroom": "groom_name",
    "GroomAge": "groom_age",
    "GroomAddress": "groom_address",
    
    # Bride fields
    "Bride": "bride_name",
    "BrideAge": "bride_age",
    "BrideAddress": "bride_address",
    
    # Wali fields
    "Wali": "wali_name",
    "WaliFather": "wali_father",
    "WaliAge": "wali_age",
    "WaliAddress": "wali_address",
    
    # Witness 1
    "Witness1": "witness1_name",
    "Witness1Age": "witness1_age",
    "Witness1Address": "witness1_address",
    
    # Witness 2
    "Witness2": "witness2_name",
    "Witness2Age": "witness2_age",
    "Witness2Address": "witness2_address",
    
    # Mahr fields
    "Mahr": "mahr_words",
    "mahr_in_figures": "mahr_figure",
    
    # Bottom section
    "bride_name_only": "bride_name",
    "groom_name_only": "groom_name",
    "mahr_in_words": "mahr_words",
    "QaziNameSeal": "qazi_name",
    "CertificateIssuePerson": "certificate_issue_person",
}

def map_form_to_print(form_data):
    """
    Convert form/database field names to print layout field names
    
    Args:
        form_data: dict with form field names as keys
        
    Returns:
        dict with print layout field names as keys
    """
    print_data = {}

    for form_key, print_key in FORM_TO_PRINT_MAPPING.items():
        value = form_data.get(print_key, "")

        if not value:
            continue  # skip empty/missing data

        # Handle special name-related fields
        if any(x in print_key.lower() for x in ['groom_name', 'bride_name', 'wali_name', 'witness1_name', 'witness2_name']):
            split_name = print_key.split("_")[0]
            father_key = f"{split_name}_father"
            age_key = f"{split_name}_age"
            address_key = f"{split_name}_address"

            father = form_data.get(father_key, "").strip()
            age = str(form_data.get(age_key, "")).strip()
            address = form_data.get(address_key, "").strip()

            # Build special formatted strings
            if form_key == 'bride_name_only':
                print_data[form_key] = f"{value} d/o {father}"
            elif form_key == 'groom_name_only':
                print_data[form_key] = f"{value} s/o {father}"
            else:
                parts = [f"{value} s/o {father}"] if split_name != 'bride' else [f"{value} d/o {father}"]
                if age:
                    parts.append(f"{age} years")
                if address:
                    parts.append(address)
                print_data[form_key] = ", ".join(parts)

        else:
            print_data[form_key] = value

    return print_data


def map_print_to_form(print_data):
    """
    Convert print layout field names back to form field names
    
    Args:
        print_data: dict with print layout field names as keys
        
    Returns:
        dict with form field names as keys
    """
    # Reverse mapping
    reverse_map = {v: k for k, v in FORM_TO_PRINT_MAPPING.items()}
    form_data = {}
    for print_key, form_key in reverse_map.items():
        if print_key in print_data:
            form_data[form_key] = print_data[print_key]

    return form_data