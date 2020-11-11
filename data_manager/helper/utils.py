def build_output(task, status, message, output):
    """Creates the generic output message of the API
    
    :param task: Type of task performed
    :type task: str
    :param status: Status of the response method
    :type status: int
    :param message: Message as result of the task performed
    :type message: str
    :param output: Output values obtained by the task performed
    :type output: dict
    :return: Generic output message with specified values, ready to be parsed as a JSON
    :rtype: dict
    """
    return {"task": task, "code": status, "message": message,
                    "output": output}