import argparse
import os
import subprocess
import shutil


imgs = []

def main():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description="An Obsidian Image bulk mover in python")

    # Specify what OS user have
    parser.add_argument("-o", "--os", help="Specify what operating system: [lnx] or [win]", required=True)
    
    # Specify the folders to be moved and extract the images.
    parser.add_argument("-m", "--move", help="Specify folder and extract image names to be moved", required=True)
    
    # Attachment folder
    parser.add_argument("-a", "--attachment", help="Specify the attachment folder to extract the needed images.", required=True)
    
    # Where to place the new images.
    parser.add_argument("-t", "--to", help="Specify the folder where it expects files", required=True)
    
    
    # Parse the command-line arguments
    args = parser.parse_args()

    if args.os == "lnx":
        
        os.chdir(args.move)
        
        command = f'grep ".*png" -h *'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, error = process.communicate()
        
        # Remove brackets
        output = output.decode()
        # Turn string into a list
        lines = output.split("\n")
    
        result_lines = [line.replace("!", "").replace("[", "").replace("]", "") for line in lines]

        # Join the modified lines back into a string
        result = '\n'.join(result_lines)

        # Print the result
        print(result)
        
        # Move to the attachment folder
        os.chdir(args.attachment)
        
        
        for file in os.listdir():
            
            if file in result:
               new_path = args.to + file
               shutil.copy(file, new_path)
            
        print("Images moved successfully.")
        
       
    else:
        print("Invalid input.")

if __name__ == "__main__":
    main()
