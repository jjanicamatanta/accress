from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
from PIL import Image
import re
import unidecode

# # ====================================================
import easyocr

@staticmethod
def imageToStringArray(image_path):
    return easyocr.Reader(['en']).readtext(image_path)

@staticmethod
def getElementByPath(driver, string_path):
    return WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.XPATH, f""+string_path))
    )

@staticmethod
def convert_to_slug(text):
    
    text = re.sub(r'\W+', '_', 
            unidecode.unidecode(text).lower()
        ).strip('_')

    return text


