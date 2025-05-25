def parse_command(user_input):
    """
    Parse the user input to identify the command and its parameters.
    """
    # Split the input into words
    words = user_input.lower().split()
    
    # Example command structure
    command = words[0] if words else None
    parameters = words[1:] if len(words) > 1 else []
    
    return command, parameters
