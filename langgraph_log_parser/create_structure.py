import os


def create_folder_structure(main_folder_name):
    """
    Create a folder structure with db, img and json subfolders.

    :param main_folder_name: Name of the main folder to be created.
    :type main_folder_name: str

    :return: True if folders were created successfully, False if the main folder already exists.
    :rtype: bool

    **Example:**

    >>> create_folder_structure("test_directory")
    Successfully created 'test_directory' with subfolders: db, img, json
    True
    """
    # Check if folder already exists
    if os.path.exists(main_folder_name):
        print(f"Error: Folder '{main_folder_name}' already exists!")
        return False

    try:
        # Create main folder
        os.makedirs(main_folder_name)

        # Create subfolders
        subfolders = ['db', 'img', 'json']
        for subfolder in subfolders:
            subfolder_path = os.path.join(main_folder_name, subfolder)
            os.makedirs(subfolder_path)

        print(f"Successfully created '{main_folder_name}' with subfolders: {', '.join(subfolders)}")
        return True

    except OSError as error:
        print(f"Error creating folder structure: {error}")
        return False