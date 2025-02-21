#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 12:38:48 2025

@author: ann
"""

import os
import requests
import json
from requests.exceptions import HTTPError, ChunkedEncodingError, ConnectionError, Timeout


def download_image(url, folder, filename, max_retries=3):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, filename)
    
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return True  
    
    retries = 0
    while retries < max_retries:
        try:
            # Download the file in chunks with a timeout
            with requests.get(url, stream=True, timeout=10) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                
                # Write the content to the file in chunks
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                
                print(f"Downloaded: {file_path}")
                return True  # Successfully downloaded
        
        except HTTPError as http_err:
            # Handle specific HTTP errors like 404
            if http_err.response.status_code == 404:
                print(f"HTTPError 404: Resource not found for URL: {url}")
                return False  # Skip this URL
            else:
                retries += 1
                print(f"HTTPError occurred: {http_err}. Retrying... Attempt {retries}/{max_retries}")
        
        except (ChunkedEncodingError, ConnectionError, Timeout) as e:
            retries += 1
            print(f"Attempt {retries}/{max_retries} failed for {url}. Error: {e}")
    
    print(f"Failed to download after {max_retries} attempts: {url}")
    return False  

if __name__ == "__main__":
    downloaded_count = 0  
    skipped_count = 0     
    
    # Load the JSON data
    with open('/home/ann/Загрузки/car-angle-type-export.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for item in data:
       
        model = item.get('model')
        angle_type = item.get('angle_type')
        url = item.get('url')
        
        if model is None or angle_type is None or url is None:
            print(f"Skipping item due to missing data: {item}")
            continue  
        
        # Create folder name
        folder_name = os.path.join(model, angle_type)
        
        # Create filename from URL
        filename = os.path.basename(url)
        
        
        if download_image(url, folder_name, filename):
            downloaded_count += 1
        else:
            if "404" in str(item):  
                skipped_count += 1
    
    print(f"Total files downloaded: {downloaded_count}")
    print(f"Total files skipped due to 404 errors: {skipped_count}")