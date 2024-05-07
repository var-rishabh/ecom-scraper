# response model
def ResponseModel(message, data):
    return {
        "status": 200,
        "message": message,
        "data": [data],
    }


# error response model
def ErrorResponseModel(status, error, message):
    return {"status": status, "error": error, "message": message}
