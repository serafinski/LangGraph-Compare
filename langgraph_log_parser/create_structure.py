import os


def create_folder_structure(main_folder_name: str) -> None:
    """
    Create a folder structure with db, img and json subfolders.

    :param main_folder_name: Name of the main folder to be created.
    :type main_folder_name: str

    **Example:**

    >>> create_folder_structure("test_directory")
    Successfully created 'test_directory' with subfolders: db, img, json
    """

    # Sprawdz czy folder istnieje
    if os.path.exists(main_folder_name):
        raise FileExistsError(f"Error: Folder '{main_folder_name}' already exists!")

    try:
        # Stworz glowny folder
        os.makedirs(main_folder_name)

        # Stworz subfoldery
        subfolders = ['db', 'img', 'json']
        for subfolder in subfolders:
            subfolder_path = os.path.join(main_folder_name, subfolder)
            os.makedirs(subfolder_path)

        print(f"Successfully created '{main_folder_name}' with subfolders: {', '.join(subfolders)}")

    except OSError as error:
        print(f"Error creating folder structure: {error}")