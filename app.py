from flask import Flask, render_template, request, redirect, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'exports'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

# Ensure exports folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


class PhoneNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    country_code = db.Column(db.String(5))
    taken = db.Column(db.Boolean, default=False)

COUNTRY_MAP = {
    'AF': 'Afghanistan',
    'AL': 'Albania',
    'DZ': 'Algeria',
    'AO': 'Angola',
    'AR': 'Argentina',
    'AM': 'Armenia',
    'AU': 'Australia',
    'AT': 'Austria',
    'AZ': 'Azerbaijan',
    'BD': 'Bangladesh',
    'BY': 'Belarus',
    'BE': 'Belgium',
    'BJ': 'Benin',
    'BO': 'Bolivia',
    'BA': 'Bosnia and Herzegovina',
    'BW': 'Botswana',
    'BR': 'Brazil',
    'BG': 'Bulgaria',
    'KH': 'Cambodia',
    'CM': 'Cameroon',
    'CA': 'Canada',
    'CL': 'Chile',
    'CN': 'China',
    'CO': 'Colombia',
    'CR': 'Costa Rica',
    'HR': 'Croatia',
    'CY': 'Cyprus',
    'CZ': 'Czech Republic',
    'DK': 'Denmark',
    'EG': 'Egypt',
    'EE': 'Estonia',
    'ET': 'Ethiopia',
    'FI': 'Finland',
    'FR': 'France',
    'GE': 'Georgia',
    'DE': 'Germany',
    'GH': 'Ghana',
    'GR': 'Greece',
    'GT': 'Guatemala',
    'HK': 'Hong Kong',
    'HU': 'Hungary',
    'IS': 'Iceland',
    'IN': 'India',
    'ID': 'Indonesia',
    'IR': 'Iran',
    'IQ': 'Iraq',
    'IE': 'Ireland',
    'IL': 'Israel',
    'IT': 'Italy',
    'JM': 'Jamaica',
    'JP': 'Japan',
    'JO': 'Jordan',
    'KZ': 'Kazakhstan',
    'KE': 'Kenya',
    'KR': 'South Korea',
    'KW': 'Kuwait',
    'KG': 'Kyrgyzstan',
    'LA': 'Laos',
    'LV': 'Latvia',
    'LB': 'Lebanon',
    'LY': 'Libya',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MG': 'Madagascar',
    'MY': 'Malaysia',
    'ML': 'Mali',
    'MX': 'Mexico',
    'MD': 'Moldova',
    'MN': 'Mongolia',
    'MA': 'Morocco',
    'MZ': 'Mozambique',
    'MM': 'Myanmar',
    'NA': 'Namibia',
    'NP': 'Nepal',
    'NL': 'Netherlands',
    'NZ': 'New Zealand',
    'NI': 'Nicaragua',
    'NE': 'Niger',
    'NG': 'Nigeria',
    'MK': 'North Macedonia',
    'NO': 'Norway',
    'OM': 'Oman',
    'PK': 'Pakistan',
    'PA': 'Panama',
    'PY': 'Paraguay',
    'PE': 'Peru',
    'PH': 'Philippines',
    'PL': 'Poland',
    'PT': 'Portugal',
    'QA': 'Qatar',
    'RO': 'Romania',
    'RU': 'Russia',
    'SA': 'Saudi Arabia',
    'RS': 'Serbia',
    'SG': 'Singapore',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'ZA': 'South Africa',
    'ES': 'Spain',
    'LK': 'Sri Lanka',
    'SD': 'Sudan',
    'SE': 'Sweden',
    'CH': 'Switzerland',
    'SY': 'Syria',
    'TW': 'Taiwan',
    'TZ': 'Tanzania',
    'TH': 'Thailand',
    'TN': 'Tunisia',
    'TR': 'Turkey',
    'UG': 'Uganda',
    'UA': 'Ukraine',
    'AE': 'United Arab Emirates',
    'GB': 'United Kingdom',
    'US': 'United States',
    'UY': 'Uruguay',
    'UZ': 'Uzbekistan',
    'VE': 'Venezuela',
    'VN': 'Vietnam',
    'YE': 'Yemen',
    'ZM': 'Zambia',
    'ZW': 'Zimbabwe',
    'CI': 'Ivory Coast'
}





@app.route('/', methods=['GET', 'POST'])
def index():
    # Get the count of available phone numbers
    total_count = PhoneNumber.query.count()
    available_count = PhoneNumber.query.filter_by(taken=False).count()

    countries = db.session.query(PhoneNumber.country_code).filter_by(taken=False).distinct().all()
    country_codes = [c[0] for c in countries]

    country_options = [(code, COUNTRY_MAP.get(code, code)) for code in country_codes]

    exported_folder_count = 0
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        exported_folder_count = len([
            f for f in os.listdir(app.config['UPLOAD_FOLDER'])
            if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))
        ])


    
    return render_template('index.html',total_count=total_count, available_count=available_count, exported_file_count=exported_folder_count, country_codes=country_options)



@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        flash('No file uploaded.')
        return redirect('/')

    new_numbers = 0
    duplicate_numbers = 0

    try:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            phone = str(row['Number']).strip()
            code = str(row['Country Short Code']).strip()
            # Check if the phone number already exists
            if not PhoneNumber.query.filter_by(phone=phone).first():
                db.session.add(PhoneNumber(phone=phone, country_code=code))
                new_numbers += 1
            else:
                duplicate_numbers += 1
        
        db.session.commit()

        # Flash the result summary
        if new_numbers > 0:
            flash(f'{new_numbers} new phone numbers added.', 'success')
        if duplicate_numbers > 0:
            flash(f'{duplicate_numbers} duplicate phone numbers were skipped.', 'warning')
    except Exception as e:
        flash(f'Error processing file: {e}', 'danger')

    return redirect('/')



@app.route('/download', methods=['POST'])
def download():
    try:
        count = int(request.form.get('count', 100))
        country_code = str(request.form.get('country', ""))
    except ValueError:
        flash("Invalid number count.")
        return redirect('/')
    if country_code is  None:
        flash(f'Error in country selction.', 'danger')
        return redirect('/')
    
    if country_code =="all":
        available_numbers = PhoneNumber.query.filter_by(taken=False).limit(count).all()
        country_name = "All"
    else:
        available_numbers = PhoneNumber.query.filter_by(taken=False,country_code=country_code).limit(count).all()
        country_name = COUNTRY_MAP.get(country_code, country_code)


    if not available_numbers:
        flash("No available numbers to export.","warning")
        return redirect('/')

    # Create the folder based on the existing folder count + 1
    folder_count = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))])
    new_folder_name = f"{folder_count + 1}-{country_name}"
    new_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], new_folder_name)

    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)


    start_id = PhoneNumber.query.filter_by(taken=True).count()

    end_id = len(available_numbers) + start_id


    data = {
        'Number': [n.phone for n in available_numbers],
        'Country Short Code': [n.country_code for n in available_numbers]
    }

    df = pd.DataFrame(data)
    filename = f"{start_id}-{end_id}.xlsx"
    filepath = os.path.join(new_folder_path, filename)
    df.to_excel(filepath, index=False)

    for number in available_numbers:
        number.taken = True
    db.session.commit()

    flash(f"Exported {len(available_numbers)} numbers to {filename}", 'info')
    
    return redirect('/')


@app.route('/git_push', methods=['POST'])
def git_push():
    try:
        # Add all changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit the changes
        subprocess.run(['git', 'commit', '-m', 'Auto commit from Flask UI'], check=True)

        # Push the changes
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)

        flash("Changes pushed successfully to GitHub!", "github")

    except subprocess.CalledProcessError as e:
        flash(f"Error during git push: {str(e)}", "github-danger")

    return redirect('/')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
