import os

def get_project_root():
    """ Returns the absolute path of the project root. """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = current_dir
    while not os.path.exists(os.path.join(root_dir, '.git')):
        # Assuming the root of the project contains the .git folder
        # If your project does not use Git, use another distinctive marker
        new_root_dir = os.path.dirname(root_dir)
        if new_root_dir == root_dir:
            # Root of the file system reached
            raise Exception("Project root not found")
        root_dir = new_root_dir
    return root_dir