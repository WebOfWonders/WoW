from django.shortcuts import render
import requests
import pytesseract
from PIL import Image
from django.core.files.storage import FileSystemStorage
import hashlib
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.conf import settings  # Import settings

#index
def index(request):
    return render(request, 'Apps/index.html')

#Weather
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



#url Shortner


# from django.shortcuts import render
# from django.http import HttpResponseRedirect
# from django.utils.crypto import get_random_string

# # In-memory dictionary to store URL mappings (for demo purposes)
# url_mapping = {}

# def shorten_url(request):
#     if request.method == 'POST':
#         original_url = request.POST.get('original_url')
#         custom_name = request.POST.get('custom_name')

#         if original_url:
#             # Use custom name if provided, otherwise, generate a random short code
#             short_code = custom_name if custom_name else get_random_string(length=6)

#             # Check if the custom short code already exists
#             if short_code in url_mapping:
#                 return render(request, 'Apps/shortener.html', {'error': 'This name is already taken!'})

#             # Store the mapping in the dictionary
#             url_mapping[short_code] = original_url

#             # Generate the shortened URL
#             short_url = f"{request.build_absolute_uri('/').rstrip('/')}/{short_code}"

#             return render(request, 'Apps/shortener.html', {'short_url': short_url})

#     return render(request, 'Apps/shortener.html')

# def redirect_url(request, short_code):
#     # Look for the original URL using the short code
#     original_url = url_mapping.get(short_code)

#     if original_url:
#         return HttpResponseRedirect(original_url)
#     else:
#         return render(request, 'Apps/shortener.html', {'error': 'Invalid short URL'})


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string

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


#video download by link

# import yt_dlp


# def download_video(request):
#     if request.method == 'POST':
#         video_url = request.POST.get('video_url')

#         if not video_url:
#             return HttpResponse("Please provide a valid video URL.", status=400)

#         try:
#             # Get the Downloads folder path dynamically
#             downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

#             # Ensure the Downloads folder exists
#             if not os.path.exists(downloads_folder):
#                 os.makedirs(downloads_folder)

#             # Configure yt-dlp options
#             ydl_opts = {
#                 'format': 'best',
#                 'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),  # Save to Downloads folder
#             }

#             # Download and extract video information
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 info_dict = ydl.extract_info(video_url, download=True)
#                 video_title = info_dict.get('title', 'video')
#                 video_duration = info_dict.get('duration', 0)  # Duration in seconds
#                 video_description = info_dict.get('description', 'No description available.')
#                 file_name = f"{video_title}.{info_dict.get('ext', 'mp4')}"
#                 downloaded_file_path = os.path.join(downloads_folder, file_name)

#             # Calculate video duration in minutes and seconds
#             duration_minutes = video_duration // 60
#             duration_seconds = video_duration % 60

#             # Pass details to the template
#             return render(request, 'Apps/download_video.html', {
#                 'file_name': file_name,
#                 'video_title': video_title,
#                 'video_duration': f"{duration_minutes} minutes {duration_seconds} seconds",
#                 'video_description': video_description,
#                 'downloaded_file_path': downloaded_file_path,
#             })

#         except Exception as e:
#             return HttpResponse(f"Error downloading video: {str(e)}", status=500)

#     return render(request, 'Apps/download_video.html')


import os
import yt_dlp
from django.shortcuts import render, redirect
from django.http import HttpResponse

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
from django.shortcuts import render
from django.http import HttpResponse
import datetime
import pytz
import pycountry  # For mapping country names to ISO codes


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
