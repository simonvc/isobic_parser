import csv
import os
import re

def parse_file(input_file, output_csv):
    # Compile a regex pattern to match date lines (YYYY-MM-DD)
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    # Compile a regex pattern to match footer lines like '3 of 3824'
    footer_pattern = re.compile(r'^\d+\s+of\s+\d+$')

    # Define a set of header lines to ignore
    ignore_lines = {
        '^LRecord',
        'creation',
        'date',
        'Last',
        'Update',
        'BIC',
        'Brch',
        'Code',
        'Full legal name',
        'Registered address',
        'Operational address'
    }

    # Check if the CSV file exists to determine if we need to write the header
    file_exists = os.path.isfile(output_csv)

    with open(input_file, 'r', encoding='utf-8') as f_input, \
         open(output_csv, 'a', newline='', encoding='utf-8') as f_output:

        lines = [line.rstrip('\n') for line in f_input]
        writer = csv.writer(f_output)

        # Write header if the file is newly created
        if not file_exists or os.path.getsize(output_csv) == 0:
            writer.writerow(['BIC8', 'Branch Code', 'Bank Name', 'Address Block 1', 'Address Block 2', 'Country', 'Institution Type'])

        # Filter out header and footer lines
        filtered_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line in ignore_lines:
                continue
            if footer_pattern.match(stripped_line):
                continue
            filtered_lines.append(line)

        lines = filtered_lines
        idx = 0
        total_lines = len(lines)

        while idx < total_lines:
            record = {
                'bic8': '',
                'branch_code': '',
                'bank_name': '',
                'address_block1': [],
                'address_block2': [],
                'country': '',
                'institution_type': ''
            }

            # Helper function to skip blank lines
            def skip_blank_lines():
                nonlocal idx
                while idx < total_lines and lines[idx].strip() == '':
                    idx += 1

            # Helper function to get the next non-blank line and its index
            def get_next_non_blank_line(start_idx):
                idx = start_idx
                while idx < total_lines:
                    line = lines[idx].strip()
                    if line != '':
                        return line, idx
                    idx += 1
                return None, idx

            # Skip blank lines at the beginning
            skip_blank_lines()
            if idx >= total_lines:
                break

            # Read two date lines
            date_lines_encountered = 0
            while date_lines_encountered < 2 and idx < total_lines:
                line = lines[idx].strip()
                if date_pattern.match(line):
                    idx += 1
                    date_lines_encountered += 1
                    skip_blank_lines()
                else:
                    # Skip non-date lines between dates
                    idx += 1
                    skip_blank_lines()

            if idx >= total_lines:
                break

            # Read BIC8
            if idx < total_lines and lines[idx].strip() != '':
                record['bic8'] = lines[idx].strip()
                idx += 1

            skip_blank_lines()

            # Read branch code
            if idx < total_lines and lines[idx].strip() != '':
                record['branch_code'] = lines[idx].strip()
                idx += 1

            skip_blank_lines()

            # Read bank name
            if idx < total_lines and lines[idx].strip() != '':
                record['bank_name'] = lines[idx].strip()
                idx += 1

            skip_blank_lines()

            # Read address block 1
            while idx < total_lines and lines[idx].strip() != '':
                if date_pattern.match(lines[idx].strip()):
                    break
                record['address_block1'].append(lines[idx].strip())
                idx += 1

            skip_blank_lines()

            # Read address block 2
            while idx < total_lines:
                line = lines[idx].strip()

                if date_pattern.match(line):
                    break

                if line == '':
                    # Check for two consecutive blank lines or date line
                    idx_temp = idx + 1
                    skip_blank_lines()
                    next_line, _ = get_next_non_blank_line(idx)
                    if idx >= total_lines or (next_line and date_pattern.match(next_line)):
                        break
                    idx = idx_temp  # Restore idx if no extra blank lines
                record['address_block2'].append(line)
                idx += 1

            skip_blank_lines()

            # Prepare to read 'Country' and 'Institution Type'

            # Get the next two non-blank lines after 'idx'
            line1, idx1 = get_next_non_blank_line(idx)
            line2, idx2 = get_next_non_blank_line(idx1 + 1 if line1 else idx1)

            next_is_date = False
            if line1 and line2 and date_pattern.match(line1) and date_pattern.match(line2):
                next_is_date = True

            if next_is_date:
                # Backtrack to find the last two non-blank, non-date lines before the date lines
                prev_lines = []
                back_idx = idx - 1
                while back_idx >= 0 and len(prev_lines) < 2:
                    line = lines[back_idx].strip()
                    if line != '' and not date_pattern.match(line):
                        prev_lines.insert(0, line)
                    back_idx -= 1
                if len(prev_lines) >= 2:
                    record['country'] = prev_lines[-2]
                    record['institution_type'] = prev_lines[-1]
                elif len(prev_lines) == 1:
                    record['institution_type'] = prev_lines[-1]
            else:
                # Read 'Country'
                if line1 and not date_pattern.match(line1):
                    record['country'] = line1
                    idx = idx1 + 1
                else:
                    idx = idx1

                skip_blank_lines()

                # Get the next non-blank line
                line, idx = get_next_non_blank_line(idx)
                if line and not date_pattern.match(line):
                    record['institution_type'] = line
                    idx += 1

            # Skip blank lines before the next record
            skip_blank_lines()

            # Write the record to CSV
            writer.writerow([
                record['bic8'],
                record['branch_code'],
                record['bank_name'],
                ' '.join(record['address_block1']),
                ' '.join(record['address_block2']),
                record['country'],
                record['institution_type']
            ])

    # End of function

# Usage example:
parse_file('ISOBIC.txt', 'ISOBIC.csv')

