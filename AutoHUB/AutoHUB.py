import os
import requests
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import smtplib
from email.message import EmailMessage
import shutil
import logging
import re
import hashlib
import datetime
import csv
import sys




logging.basicConfig(
    filename='AutoHub.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',\
    level=logging.INFO
)


def auto_file_renamer():
    try:
        folder = input("Enter the folder path: ").strip()
        prefix = input("Enter the prefix for renaming files: ").strip()
        ext_filter = input("Enter the file extension to filter (e.g., .txt, .jpg) or (leave blank for no filter): ").strip().lower()

        if not os.path.exists(folder):
            print("The specified folder does not exist.")
            
            return
        counter = 1

        for file in os.listdir(folder):
            path = os.path.join(folder, file)

            name, ext = os.path.splitext(file)

            if ext_filter and ext.lower() != ext_filter:
                continue

            
            new_name = f"{prefix}_{counter}{ext}"
            new_path = os.path.join(folder, new_name)
            try:
                os.rename(path, new_path)
                print(f"Renamed: {file} --> {new_name}")
                counter += 1
            except Exception as e:
                print(f"Could Not Rename {file} Due To Error : {e}")

        print(f"renamed {counter - 1} files")
        logging.info(f"renamed {counter - 1} files in {folder}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in auto_file_renamer: {e}")


def bulk_image_resizer():
    try:
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
        new_width = 800
        target = input("Enter the folder path containing images: ").strip()
        output = "resized_images"
        os.makedirs(output, exist_ok=True)

        if not os.path.exists(target):
            print("The specified folder does not exist.")
            
            return
        counter = 0

        for file in os.listdir(target):
            path = os.path.join(target, file)
            
            
            if os.path.isdir(path):
                continue

            name, ext = os.path.splitext(file)
            if ext.lower() not in image_extensions:
                continue

            try:
                try:
                    img = Image.open(path)
                except OSError:
                    print(f"Skipping unsupported image file: {file}")
                    logging.warning(f"Skipping unsupported image file: {file} in {target}")
                    continue

                image_width, image_height = img.size
                new_height = int((new_width / image_width) * image_height)
                new_img = img.resize((new_width, new_height))

                new_path = os.path.join(output, file)
                new_img.save(new_path)
                print(f"Resized and saved: {file} --> {new_path}")
                counter += 1
                
            except Exception as e:
                print(f"Failed to process {file}: {e}")
                logging.error(f"Failed to process {file} in {target}: {e}")
        print(f"Resized {counter} images")
        logging.info(f"Resized {counter} images in {target}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in bulk_image_resizer: {e}")


def bulk_text_renamer():
    try:
        folder = input("Enter the folder path: ").strip()
        target_text = input("Enter the text to be replaced: ").strip()
        replacement_text = input("Enter the replacement text: ").strip()
        ext_filter = "txt"

        if not os.path.exists(folder):
            print("The specified folder does not exist.")
            return

        total_replacements = 0

        for file in os.listdir(folder):
            path = os.path.join(folder, file)

            if os.path.isdir(path):
                continue

            name, ext = os.path.splitext(file)
            if ext.lower() != f".{ext_filter}":
                continue

            shutil.copy(path, path + ".bak")

            try:
                with open(path, 'r', encoding='UTF-8') as f:
                    content = f.read()

                updated_content, num_replacements = re.subn(target_text, replacement_text, content, flags=re.IGNORECASE)

                with open(path, 'w', encoding='UTF-8') as f:
                    f.write(updated_content)

                total_replacements += num_replacements
                print(f"Replaced {num_replacements} occurrences in {file}")

            except Exception as e:
                print(f"Failed to process {file}: {e}")
                logging.error(f"Failed to process {file} in {folder}: {e}")

        print(f"Total replacements made: {total_replacements}")
        logging.info(f"Total replacements made: {total_replacements} in {folder}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in bulk_text_renamer: {e}")


def email_sender():
    try:
        sender = input("Enter your email address: ").strip()
        app_key = input("Enter your app password: ").strip()
        recipient = input("Enter the recipient's email address: ").strip()
        subject = input("Enter the email subject: ").strip()
        body = input("Enter the email body: ").strip()


        msg = EmailMessage()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.set_content(body)

        attachment = input("Enter the file path to attach (or leave blank for no attachment): ").strip()

        if attachment:
            try:
                with open(attachment, 'rb') as f:
                    file_data = f.read()
                    file_name = os.path.basename(attachment)
                    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

                print(f"Attached file: {file_name}")
            except Exception as e:
                print(f"Failed to attach file: {e}")
                logging.error(f"Failed to attach file {attachment}: {e}")
                return
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(sender, app_key)
                smtp.send_message(msg)
                print("Email sent successfully!")
                logging.info(f"Email sent to {recipient} from {sender}")
        except Exception as e:
            print(f"Failed to send email: {e}")
            logging.error(f"Failed to send email to {recipient} from {sender}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in email_sender: {e}")

def empty_directory_scanner():
    try:
        target = input("Enter the folder path to scan for empty directories: ").strip()
        empty_dirs = []

        if not os.path.exists(target):
            print("The specified folder does not exist.")
            
            return

        for foldername, subfolders, filenames in os.walk(target):
            if not os.listdir(foldername):
                try:
                    os.rmdir(foldername)
                    empty_dirs.append(foldername)
                    print(f"Removed empty directory: {foldername}")
                except Exception as e:
                    print(f"Failed to remove {foldername}: {e}")
                    logging.error(f"Failed to remove {foldername}: {e}")

        if empty_dirs:
            print(f"Removed {len(empty_dirs)} empty directories.")
            logging.info(f"Removed {len(empty_dirs)} empty directories in {target}")
        else:
            print("No empty directories found.")
            logging.info(f"No empty directories found in {target}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in empty_directory_scanner: {e}")



def file_mover():
    try:
        target = input("Enter the source folder path: ").strip()
        
        if not os.path.exists(target):
            print("The specified source folder does not exist.")
            
            return

        copyto = input("Enter the destination folder path: ").strip()
        if not os.path.exists(copyto):
            os.makedirs(copyto)
            print(f"Created destination folder: {copyto}")
        moved_files = 0

        for file in os.listdir(target):
            path = os.path.join(target, file)

            if os.path.isdir(path):
                continue

            try:
                copy_path = os.path.join(copyto, file)
                shutil.copy2(path, copy_path)

                name, ext = os.path.splitext(file)
                renamed = f"{name}_copy{ext}"
                renamed_path = os.path.join(copyto, renamed)
                os.rename(copy_path, renamed_path)
                print(f"Copied and renamed: {file} --> {renamed}")
                moved_files += 1
                logging.info(f"Copied and renamed {file} to {renamed} in {copyto}")

                os.remove(path)
                logging.info(f"Removed original file {file} from {target}")
                print(f"processed {moved_files} files")

            except Exception as e:
                print(f"Failed to process {file}: {e}")
                logging.error(f"Failed to process {file} in {target}: {e}")

        print(f"processed {moved_files} files")
        logging.info(f"Processed {moved_files} files from {target} to {copyto}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in file_mover: {e}")


def file_organizer():
    try:
        target = input("Enter the folder path to organize: ").strip()
        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return

        file_types = {
            "Images": [".jpg", ".png", ".jpeg", ".gif"],
            "Documents": [".pdf", ".docx", ".txt"],
            "Videos": [".mp4", ".mov"],
            "Archives": [".zip", ".rar", ".tar"],
            "Code": [".py", ".js", ".html"]
        }

        moved_counter = 0  # initialize counter outside the loop

        for file in os.listdir(target):
            path = os.path.join(target, file)

            if os.path.isdir(path):
                continue

            _, ext = os.path.splitext(file)
            moved = False

            for folder, extensions in file_types.items():
                if ext.lower() in extensions:
                    try:
                        destination = os.path.join(target, folder)
                        os.makedirs(destination, exist_ok=True)
                        shutil.move(path, os.path.join(destination, file))
                        print(f"Moved: {file} --> {folder}/")
                        logging.info(f"Moved {file} to {folder} in {target}")
                        moved = True
                        moved_counter += 1
                        break
                    except Exception as e:
                        print(f"Could not move {file} due to error: {e}")
                        logging.error(f"Failed to move {file} in {target}: {e}")

            if not moved:
                print(f"No matching folder for: {file} (unknown type)")

        print(f"Moved {moved_counter} files in total.")
        logging.info(f"Moved {moved_counter} files in {target}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in file_organizer: {e}")




def duplicate_file_finder():
    try:
        def get_hash(path):
            try:
                hasher = hashlib.md5()
                with open(path, 'rb') as f:
                    while chunk := f.read(4096):
                        hasher.update(chunk)
                return hasher.hexdigest()
            except Exception as e:
                print(f"Unable to get file hash for '{path}' due to error: {e}")
                logging.error(f"Unable to get file hash for '{path}' due to error: {e}")
                return None  # <-- Fix: return None if hashing fails

        file_hashes = {}
        dupes = []

        target = input("Enter the folder path to scan for duplicate files: ").strip()
        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return

        for foldername, subfolders, filenames in os.walk(target):
            for filename in filenames:
                path = os.path.join(foldername, filename)

                hash_val = get_hash(path)
                if hash_val is None:
                    continue  # Skip files that couldn't be hashed

                if hash_val in file_hashes:
                    dupes.append((path, file_hashes[hash_val]))
                else:
                    file_hashes[hash_val] = path

        if dupes:
            print("Duplicates found:")
            for dup, original in dupes:
                print(f"Duplicate: {dup} (Original: {original})")
                logging.info(f"Duplicate found: {dup} (Original: {original})")
        else:
            print("No duplicate files found.")
            logging.info(f"No duplicate files found in {target}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in duplicate_file_finder: {e}")



def meta_data_retriever():
    try:
        target = input("Enter the folder path to scan for files: ").strip()
        csv_file = "file_metadata.csv"

        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return

        # Open the CSV once and write all metadata inside the same block
        with open(csv_file, 'w', newline='', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["File Name", "Size (KB)", "Created", "Modified", "Accessed", "Type"])

            for file in os.listdir(target):
                path = os.path.join(target, file)

                if os.path.isdir(path):
                    continue

                try:
                    name, ext = os.path.splitext(file)
                    size = os.path.getsize(path) / 1024
                    created = datetime.datetime.fromtimestamp(os.path.getctime(path))
                    modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                    accessed = datetime.datetime.fromtimestamp(os.path.getatime(path))

                    writer.writerow([file, f"{size:.2f}", created, modified, accessed, ext])
                    print(f"Processed metadata for: {file}")
                    logging.info(f"Processed metadata for {file} in {target}")

                except Exception as e:
                    print(f"Failed to process {file}: {e}")
                    logging.error(f"Failed to process {file} in {target}: {e}")

        print(f"Metadata saved to {csv_file}")
        logging.info(f"Metadata saved to {csv_file} in {target}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in meta_data_retriever: {e}")



def folder_backup():
    try:
        target = input("Enter the folder path to back up: ").strip()
        destination = input("Enter the backup destination folder path: ").strip()

        if not os.path.exists(target):
            print("The specified source folder does not exist.")
            return

        for foldername, subfolders, filenames in os.walk(target):
            for filename in filenames:
                source_path = os.path.join(foldername, filename)
                relative_path = os.path.relpath(foldername, target)
                dest_folder = os.path.join(destination, relative_path)
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, filename)
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"Backed up: {source_path} --> {dest_path}")
                    logging.info(f"Backed up {source_path} to {dest_path}")
                except Exception as e:
                    print(f"Failed to back up {source_path}: {e}")
                    logging.error(f"Failed to back up {source_path} to {dest_path}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in folder_backup: {e}")


def image_converter():
    try:
        target = input("Enter the folder path: ").strip()
        choice = input("Convert from (1) JPG to PNG or (2) PNG to JPG? Enter 1 or 2: ").strip()
        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return

        if choice == "1":
            source_ext = ".jpg"
            target_ext = ".png"
        elif choice == "2":
            source_ext = ".png"
            target_ext = ".jpg"
        else:
            print("Invalid choice")
            return

        output_folder = os.path.join(target, "converted")
        os.makedirs(output_folder, exist_ok=True)

        for file in os.listdir(target):
            file_path = os.path.join(target, file)

            if os.path.isdir(file_path):
                continue

            name, ext = os.path.splitext(file)
            if ext.lower() != source_ext:
                continue

            try:
                img = Image.open(file_path)
                if target_ext == ".jpg":
                    img = img.convert("RGB")
                new_name = name + target_ext
                new_path = os.path.join(output_folder, new_name)
                img.save(new_path)
                print(f"Converted {file} → {new_name}")
                logging.info(f"Converted {file} to {new_name} in {output_folder}")
            except Exception as e:
                print(f"Failed to convert {file}: {e}")
                logging.error(f"Failed to convert {file} in {target}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in image_converter: {e}")

def extension_renamer():
    try:
        target = input("Enter the folder path: ").strip()
        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return
        from_ext = input("Enter the current file extension (e.g., .txt): ").strip().lower().split(',')
        from_ext = [f".{ext.strip()}" for ext in from_ext]

        to_ext = input("Enter the new file extension (e.g., .md): ").strip().lower()
        if not to_ext.startswith('.'):
            to_ext = '.' + to_ext

        

        for file in os.listdir(target):
            path = os.path.join(target, file)

            if os.path.isdir(path):
                continue

            name, ext = os.path.splitext(file)

            if ext.lower() in from_ext:
                new_name = name + to_ext
                new_path = os.path.join(target, new_name)

                try:
                    os.rename(path, new_path)
                    print(f"Renamed: {file} --> {new_name}")
                    logging.info(f"Renamed {file} to {new_name} in {target}")
                except Exception as e:
                    print(f"Failed to rename {file}: {e}")
                    logging.error(f"Failed to rename {file} in {target}: {e}")
        print("Renaming completed.")
        logging.info(f"Completed renaming files in {target}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in extension_renamer: {e}")

def pdf_merger():
    try:
        target = input("Enter the folder path containing PDFs: ").strip()
        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return
        output_pdf = input("Enter the output PDF file name (e.g., merged.pdf): ").strip()

        merger = PdfMerger()

        for foldername, subfolders, filenames in os.walk(target):
            for filename in sorted(filenames):
                if filename.lower().endswith('.pdf'):
                    path = os.path.join(foldername, filename)
                    try:
                        merger.append(path)
                        print(f"Added: {filename}")
                        logging.info(f"Added {filename} to merger from {foldername}")
                    except Exception as e:
                        print(f"Failed to add {filename}: {e}")
                        logging.error(f"Failed to add {filename} from {foldername}: {e}")
        
        output_path = os.path.join(target, output_pdf)
        merger.write(output_path)
        merger.close()
        print(f"Merged PDF saved as: {output_path}")
        logging.info(f"Merged PDF saved as {output_path} in {target}")
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in pdf_merger: {e}")

def pdf_splitter():
    try:
        target = input("Enter the folder path containing PDFs: ").strip()
        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return
        
        output = os.path.join(target, "split_pdfs")
        os.makedirs(output, exist_ok=True)

        for filename in os.listdir(target):
            if not filename.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(target, filename)
            reader = PdfReader(file_path)

            for i, page in enumerate(reader.pages, start=1):
                writer = PdfWriter()
                writer.add_page(page)

                output_path = os.path.join(output, f"{os.path.splitext(filename)[0]}_page_{i}.pdf")
                with open(output_path, 'wb') as f:
                    writer.write(f)

                print(f"Created: {output_path}")
                logging.info(f"Created split PDF {output_path} from {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in pdf_splitter: {e}")


def screenshot_renamer_mover():
    try:
        target = input("Enter the folder path containing screenshots: ").strip()
        if not os.path.exists(target):
            print("The specified folder does not exist.")
            return
        screenshot_folder = os.path.join(target, "Screenshots")
        os.makedirs(screenshot_folder, exist_ok=True)

        prefix = "Screenshot"
        counter = 1

        for file in os.listdir(target):
            path = os.path.join(target, file)

            if os.path.isdir(path):
                continue

            name, ext = os.path.splitext(file)
            if "screenshot" in name.lower() and ext.lower() == ".png":
                dest_path = os.path.join(screenshot_folder, file)
                shutil.move(path, dest_path)
                print(f"Moved: {file} --> Screenshots/")
                logging.info(f"Moved {file} to Screenshots in {target}")

        for filename in os.listdir(screenshot_folder):
            file_path = os.path.join(screenshot_folder, filename)

            if os.path.isdir(file_path):
                continue

            _, ext = os.path.splitext(filename)
            new_name = f"{prefix}_{counter}{ext}"
            new_path = os.path.join(screenshot_folder, new_name)
            os.rename(file_path, new_path)
            print(f"Renamed: {filename} --> {new_name}")
            logging.info(f"Renamed {filename} to {new_name} in {screenshot_folder}")
            counter += 1
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in Screenshot moving and renaming: {e}")



def server_status_checker():
    try:
        path = input("Enter the file path containing URLs (one per line): ").strip()
        if not os.path.exists(path):
            print("The specified file does not exist.")
            return

        with open(path, 'r') as file:
            sites = [line.strip() for line in file if line.strip()]

        if not sites:
            print("No URLs found in the file.")
            return

        for site in sites:
            if not site.startswith(("http://", "https://")):
                site = "http://" + site  # fallback to http

            try:
                response = requests.get(site, timeout=5)
                if response.status_code == 200:
                    print(f"{site} is Online")
                    logging.info(f"{site} is online")
                else:
                    print(f"{site} returned status code: {response.status_code}")
                    logging.warning(f"{site} returned status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"{site} is offline or unreachable ({e})")
                logging.error(f"{site} is offline or unreachable: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"An error occurred in server_status_checker: {e}")




def main_menu():
    # 44 61 72 6B 69 73 73 6B 79 #
    print("===============================")
    print("           AutoHUB             ")
    print("===============================")
    print('')
    print('')
    print('')
    print('')

    print('1. Auto File Renamer')
    print('')
    print('2. Bulk Image Resizer')
    print('')
    print('3. Bulk Text Renamer')
    print('')
    print('4. Email Sender')
    print('')
    print('5. Empty Directory Scanner')
    print('')
    print('6. File Mover')
    print('')
    print('7. File Organiser')
    print('')
    print('8. Duplicate File Scanner')
    print('')
    print('9. File Metadata Retriever')
    print('')
    print('10. Folder Backup')
    print('')
    print('11. Image Converter')
    print('')
    print('12. Extension Renamer')
    print('')
    print('13. PDF Merger')
    print('')
    print('14. PDF Splitter')
    print('')
    print('15. Screenshot Renamer and Mover')
    print('')
    print('16. Server Status Checker')
    print('')
    print('17. Exit Program')

    return int(input("Enter An Action To Perform: "))


while True:
    choice = main_menu()

    if choice == 1:
        auto_file_renamer()
    elif choice == 2:
        bulk_image_resizer()
    elif choice == 3:
        bulk_text_renamer()
    elif choice == 4:
        email_sender()
    elif choice == 5:
        empty_directory_scanner()
    elif choice == 6:
        file_mover()
    elif choice == 7:
        file_organizer()
    elif choice == 8:
        duplicate_file_finder()
    elif choice == 9:
        meta_data_retriever()
    elif choice == 10:
        folder_backup()
    elif choice == 11:
        image_converter()
    elif choice == 12:
        extension_renamer()
    elif choice == 13:
        pdf_merger()
    elif choice == 14:
        pdf_splitter()
    elif choice == 15:
        screenshot_renamer_mover()
    elif choice == 16:
        server_status_checker()
    elif choice == 17:
        print("Exiting Program")
        sys.exit()
    else:
        print("Please Enter A Proper Value (1-17)")

