def validate_form_fields(form_fields, request_form):
    for form_field in form_fields:
        if form_field not in request_form:
            return False, form_field

    return True