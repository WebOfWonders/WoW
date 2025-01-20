from django.shortcuts import render, redirect
import requests
import pytesseract
from PIL import Image
from django.core.files.storage import FileSystemStorage
import hashlib
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.conf import settings  # Import settings
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
import os
import yt_dlp
import datetime
import pytz
import pycountry 
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from pymongo import MongoClient
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
import  random 
from django.core.mail import EmailMessage







#index

def index(request):
    return render(request, 'Apps/index.html')

def dashboard(request):
    return render(request, 'Apps/dashboard.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # MongoDB setup
        client = MongoClient('localhost', 27017)
        db = client['webofwonders']
        user_collection = db['User']

        # Fetch user from MongoDB
        user = user_collection.find_one({'email': email})

        if user:
            # Check if the provided password matches the hashed password
            if check_password(password, user['password']):
                # Set session or handle login success
                request.session['user'] = email
                messages.success(request, "Login successful!")
                return redirect('/dashboard/')
            else:
                messages.error(request, "Invalid password.")
        else:
            messages.error(request, "No account found with this email.")

    return render(request, 'Apps/login.html')


# Connect to MongoDB
client = MongoClient('localhost', 27017)  # Update if MongoDB is hosted elsewhere
db = client['webofwonders']  # Replace with your database name
user_collection = db['User']  # Replace with your collection name

otp_storage = {}  # Temporary OTP storage

def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the email already exists in the database
        existing_user = user_collection.find_one({"email": email})
        if existing_user:
            messages.error(request, "This email is already registered.")
            return render(request, 'Apps/register.html')  # Redirect back to registration page

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)
        otp_storage[email] = otp  # Store OTP for verification

        # HTML email content
        email_subject = "WebOfWonders - Your OTP Code"
        email_body = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 20px; background-color: #f9f9f9;">
                <h2 style="text-align: center; color: #007bff;">WebOfWonders OTP Verification</h2>
                <p>Dear User,</p>
                <p>Thank you for registering with us. Please use the following OTP to verify your email address:</p>
                <h3 style="text-align: center; color: #007bff; font-size: 28px;">{otp}</h3>
                <p>This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                <p>Regards,</p>
                <p>WebOfWonders Team</p>
            </div>
            <p style="color:'blue';">&copy; webofwonders 2025</p>
        </body>
        </html>
        """

        # Send email with OTP
        try:
            email_message = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            email_message.content_subtype = "html"  # Use HTML content type
            email_message.send(fail_silently=False)
        except Exception as e:
            messages.error(request, f"Failed to send OTP. Error: {str(e)}")
            return render(request, 'Apps/register.html')

        # Save email and password in session for OTP verification
        request.session['email'] = email
        request.session['password'] = password

        return redirect('/otp/')  # Redirect to the OTP page

    return render(request, 'Apps/register.html')



def otp_verify(request):
    if request.method == "POST":
        email = request.session.get('email')
        password = request.session.get('password')
        entered_otp = (
            request.POST.get('otp1', '') +
            request.POST.get('otp2', '') +
            request.POST.get('otp3', '') +
            request.POST.get('otp4', '') +
            request.POST.get('otp5', '') +
            request.POST.get('otp6', '')
)
        if email and entered_otp:
            correct_otp = otp_storage.get(email)
            if str(correct_otp) == entered_otp:
                # Hash the password before saving it to the database
                hashed_password = make_password(password)

                # Save the user to the MongoDB collection
                user_collection.insert_one({
                    'email': email,
                    'password': hashed_password
                })

                # Clear OTP after successful registration
                del otp_storage[email]
                messages.success(request, "Registration successful!")
                return redirect('/dashboard/')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        else:
            messages.error(request, "Session expired. Please register again.")
            return redirect('/register/')

    return render(request, 'Apps/otp.html')

#resend 

def resend_otp(request):
    if request.method == "POST":
        email = request.session.get("email", None)  # Retrieve the email from the session

        if email:
            # Generate a new OTP
            otp = random.randint(100000, 999999)
            otp_storage[email] = otp  # Store the new OTP in the temporary storage

            # HTML email content
            email_subject = "WebOfWonders - Your OTP Code"
            email_body = f"""
            <!DOCTYPE html>
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 20px; background-color: #f9f9f9;">
                    <h2 style="text-align: center; color: #007bff;">WebOfWonders OTP Verification</h2>
                    <p>Dear User,</p>
                    <p>We have generated a new OTP for you. Please use the following OTP to verify your email address:</p>
                    <h3 style="text-align: center; color: #007bff; font-size: 28px;">{otp}</h3>
                    <p>This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                    <p>Regards,</p>
                    <p>WebOfWonders Team</p>
                </div>
                <p style="color:'blue';">&copy; webofwonders 2025</p>
            </body>
            </html>
            """

            # Send email with the new OTP
            try:
                email_message = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[email],
                )
                email_message.content_subtype = "html"  # Use HTML content type
                email_message.send(fail_silently=False)
                messages.success(request, "A new OTP has been sent to your email.")
            except Exception as e:
                messages.error(request, f"Failed to resend OTP. Error: {str(e)}")
        else:
            messages.error(request, "No email associated with this session.")

    return redirect('/otp/')  # Redirect to the OTP page after attempting to resend OTP


def weather(request):
    if request.method == "POST":
        city = request.POST['city']
        api_key = 'cb92c2105916474a94d60338242112'  # Your WeatherAPI key
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no'

        # Make the API request
        response = requests.get(url)
        data = response.json()

        if 'error' not in data:  # Check if there's an error in the response
            # Extract weather data
            weather_data = {
                'temperature': data['current']['temp_c'],  # Temperature in Celsius
                'pressure': data['current']['pressure_mb'],  # Pressure in mb
                'humidity': data['current']['humidity'],  # Humidity in %
                'description': data['current']['condition']['text'],  # Weather description
                'city': city
            }
            return render(request, 'Apps/weather.html', {'weather_data': weather_data})
        else:
            error_message = "City not found or invalid API key."
            return render(request, 'Apps/weather.html', {'error_message': error_message})

    return render(request, 'Apps/weather.html')


#ocr
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path to where Tesseract is installed

def ocr(request):
    extracted_text = ''

    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        # Use pytesseract to extract text from the uploaded image
        img = Image.open(fs.path(filename))
        extracted_text = pytesseract.image_to_string(img)

        return render(request, 'Apps/ocr.html', {'file_url': file_url, 'extracted_text': extracted_text})

    return render(request, 'Apps/ocr.html')

dynamic_storage = {}


#md5

def md5(request):
    hash_value = None
    original_string = None

    if request.method == "POST":
        # Handle MD5 Hash Generation
        if "generate_hash" in request.POST:
            text = request.POST.get("text")
            if text:
                hash_value = hashlib.md5(text.encode()).hexdigest()
                # Save the text and its hash for reverse lookup
                dynamic_storage[hash_value] = text
        
        # Handle MD5 to Original String Conversion
        elif "get_original" in request.POST:
            md5_hash = request.POST.get("md5")
            if md5_hash:
                original_string = dynamic_storage.get(md5_hash, "Original string not found")

    return render(request, 'Apps/md5.html', {
        'hash_value': hash_value,
        'original_string': original_string,
    })



#nearby finder
def nearby(request):
    if request.method == "POST":
        city = request.POST.get('city')
        place = request.POST.get('place')

        if not city or not place:
            return render(request, 'Apps/nearby.html', {'error_message': 'City and Place fields are required.'})

        # Nominatimm API URL for searching places within the city
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={place}+in+{city}&limit=20"

        headers = {
            "User-Agent": "NearbyApp/1.0 (ramakrishnant684@gmail.com)"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()

            if not data:
                return render(request, 'Apps/nearby.html', {'error_message': 'No nearby places found.'})

            places = []
            for place_data in data:
                full_name = place_data['display_name']
                
                # Extract only the place name (first part before a comma)
                name = full_name.split(',')[0]

                # Use the full address
                address = full_name

                lat = place_data['lat']
                lon = place_data['lon']

                # Prepare the Google Maps link for each place
                google_map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                # Add place data
                places.append({
                    "name": name,
                    "address": address,
                    "google_map_link": google_map_link
                })

            if not places:
                return render(request, 'Apps/nearby.html', {'error_message': f'No places found for "{place}" in {city}.'})

            return render(request, 'Apps/nearby.html', {'places': places, 'place': place, 'city': city})

        except requests.exceptions.RequestException as e:
            return render(request, 'Apps/nearby.html', {'error_message': f"Error fetching data from the API: {e}"})

    return render(request, 'Apps/nearby.html')


# In-memory dictionary to store URL mappings (for demo purposes)
url_mapping = {}

def shorten_url(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        custom_name = request.POST.get('custom_name')

        if original_url:
            # Use custom name if provided, otherwise, generate a random short code
            short_code = custom_name if custom_name else get_random_string(length=6)

            # Check if the custom short code already exists
            if short_code in url_mapping:
                return render(request, 'Apps/shortener.html', {'error': 'This name is already taken!'})

            # Store the mapping in the dictionary
            url_mapping[short_code] = original_url

            # Generate the shortened URL
            short_url = f"{request.scheme}://{request.get_host()}/{short_code}"

            return render(request, 'Apps/shortener.html', {'short_url': short_url})

    return render(request, 'Apps/shortener.html')

def redirect_url(request, short_code):
    # Look for the original URL using the short code
    original_url = url_mapping.get(short_code)

    if original_url:
        return HttpResponseRedirect(original_url)
    else:
        return render(request, 'Apps/shortener.html', {'error': 'Invalid short URL'})



#Video download 

def download_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')

        if not video_url:
            return HttpResponse("Please provide a valid video URL.", status=400)

        try:
            # Get the Downloads folder path dynamically
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

            # Ensure the Downloads folder exists
            if not os.path.exists(downloads_folder):
                os.makedirs(downloads_folder)

            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),  # Save to Downloads folder
            }

            # Download and extract video information
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                video_title = info_dict.get('title', 'video')
                video_duration = info_dict.get('duration', 0)  # Duration in seconds
                video_description = info_dict.get('description', 'No description available.')
                file_name = f"{video_title}.{info_dict.get('ext', 'mp4')}"
                downloaded_file_path = os.path.join(downloads_folder, file_name)

            # Calculate video duration in minutes and seconds
            duration_minutes = video_duration // 60
            duration_seconds = video_duration % 60

            # Build the redirect URL with query parameters
            redirect_url = f'/downloadsuccess/?file_name={file_name}&video_title={video_title}&video_duration={duration_minutes} minutes {duration_seconds} seconds&video_description={video_description}&downloaded_file_path={downloaded_file_path}'

            # Redirect to the success page with the parameters
            return redirect(redirect_url)

        except Exception as e:
            return HttpResponse(f"Error downloading video: {str(e)}", status=500)

    return render(request, 'Apps/download_video.html')


def downloadsuccess(request):
    file_name = request.GET.get('file_name')
    video_title = request.GET.get('video_title')
    video_duration = request.GET.get('video_duration')
    video_description = request.GET.get('video_description')
    downloaded_file_path = request.GET.get('downloaded_file_path')

    return render(request, 'Apps/downloadsuccess.html', {
        'file_name': file_name,
        'video_title': video_title,
        'video_duration': video_duration,
        'video_description': video_description,
        'downloaded_file_path': downloaded_file_path,
    })


#stopwatch and international timing

def timing(request):
    return render(request, 'Apps/base.html')
def stopwatch(request):
    return render(request, 'Apps/stopwatch.html')
def timer(request):
    return render(request,'Apps/timer.html')




def get_country_iso(country_name):
    try:
        # Search for the country using pycountry
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_2
    except LookupError:
        return None
def international_time(request):
    if request.method == 'POST':
        country_name = request.POST.get('country_name', '').strip()

        # Get the ISO country code for the provided country name
        iso_code = get_country_iso(country_name)

        if not iso_code:
            return HttpResponse(f"Error: Invalid country name '{country_name}'", status=400)

        # Get the timezone for the ISO country code
        try:
            timezone = pytz.country_timezones.get(iso_code)
            if not timezone:
                raise ValueError("No timezone found for the country")

            # Get current time in the selected country's timezone
            current_time = datetime.datetime.now(pytz.timezone(timezone[0]))

            # Format the time to send to the template (same for both clocks)
            digital_time = current_time.strftime('%H:%M:%S')
            analog_time = current_time.strftime('%I:%M:%S %p')
            country_time = current_time.strftime('%H:%M:%S')  # same format for JS to read

            return render(request, 'Apps/international_time.html', {
                'country_name': country_name.upper(),
                'digital_time': digital_time,
                'analog_time': analog_time,
                'country_time': country_time,  # Pass the current country time to JS
                'timezone': timezone[0]  # Pass the timezone for JS to calculate
            })
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=400)

    return render(request, 'Apps/international_time_form.html')
