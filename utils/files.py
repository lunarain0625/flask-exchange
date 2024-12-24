def read_log_file(file_path):
    try:
        with open(file_path, 'r') as log_file:
            content = log_file.read()
        return content
    except FileNotFoundError:
        return f"Error: Log file '{file_path}' not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"
