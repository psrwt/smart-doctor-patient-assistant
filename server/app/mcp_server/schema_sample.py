[
    Tool(
        name='get_doctors',
        title=None,
        description='Fetches a list of all registered doctors in the system.\nUse this tool when the user wants to see which doctors are available.',
        inputSchema={
            'properties': {},
            'type': 'object'
        },
        outputSchema={
            'additionalProperties': True,
            'type': 'object'
        },
        icons=None,
        annotations=None,
        meta={'_fastmcp': {'tags': []}},
        execution=None
    ),
    Tool(
        name='find_doctor',
        title=None,
        description="Finds a specific doctor's unique ID and profile using their name.\nUse this tool IMMEDIATELY when a user mentions a doctor's name (e.g., 'Dr. Smith' or 'Ahuja').\nYou MUST have the doctor_id returned by this tool before you can check slots or book appointments.",
        inputSchema={
            'properties': {
                'name': {'type': 'string'}
            },
            'required': ['name'],
            'type': 'object'
        },
        outputSchema={
            'additionalProperties': True,
            'type': 'object'
        },
        icons=None,
        annotations=None,
        meta={'_fastmcp': {'tags': []}},
        execution=None
    ),
    Tool(
        name='get_available_slots',
        title=None,
        description="Retrieves available 1-hour appointment windows for a specific doctor on a specific date.\nTrigger this when a user selects a doctor and asks 'When is he free?' or 'Check slots for tomorrow'.\n:param doctor_id: The UUID of the doctor (get this from find_doctor).\n:param date_str: The date in YYYY-MM-DD format (IST).",
        inputSchema={
            'properties': {
                'doctor_id': {'type': 'string'},
                'date_str': {'type': 'string'}
            },
            'required': ['doctor_id', 'date_str'],
            'type': 'object'
        },
        outputSchema={
            'additionalProperties': True,
            'type': 'object'
        },
        icons=None,
        annotations=None,
        meta={'_fastmcp': {'tags': []}},
        execution=None
    ),
    Tool(
        name='book_new_appointment',
        title=None,
        description="Finalizes and books a medical appointment in the database and Google Calendar.\nUse this ONLY after the user has confirmed a specific time slot from get_available_slots.\n:param start_at: The ISO format start time (e.g., '2026-01-25T14:00:00+05:30') provided by the slot tool.\n:param symptoms: A brief description of the patient's condition.",
        inputSchema={
            'properties': {
                'doctor_id': {'type': 'string'},
                'patient_id': {'type': 'string'},
                'start_at': {'type': 'string'},
                'symptoms': {'type': 'string'}
            },
            'required': ['doctor_id', 'patient_id', 'start_at', 'symptoms'],
            'type': 'object'
        },
        outputSchema={
            'additionalProperties': True,
            'type': 'object'
        },
        icons=None,
        annotations=None,
        meta={'_fastmcp': {'tags': []}},
        execution=None
    ),
    Tool(
        name='get_doctor_appointments_by_date_range',
        title=None,
        description="Fetches a summary of appointments for a doctor within a specific date range.\nUse this when a doctor asks 'What does my week look like?' or 'List my appointments for today'.\nThis groups appointments by date and provides complete appointment informatino with slot times, patient names and symptoms.\n:param doctor_id: The UUID of the doctor.\n:param start_date_str: The start date in YYYY-MM-DD format.\n:param end_date_str: The end date in YYYY-MM-DD format.\nReturns a summary including total count and a schedule breakdown.",
        inputSchema={
            'properties': {
                'doctor_id': {'type': 'string'},
                'start_date_str': {'type': 'string'},
                'end_date_str': {'type': 'string'}
            },
            'required': ['doctor_id', 'start_date_str', 'end_date_str'],
            'type': 'object'
        },
        outputSchema={
            'additionalProperties': True,
            'type': 'object'
        },
        icons=None,
        annotations=None,
        meta={'_fastmcp': {'tags': []}},
        execution=None
    ),
    Tool(
        name='search_appointments_by_symptom_keyword',
        title=None,
        description="Searches for appointments where the patient's symptoms match a keyword.\nUse this for clinical reporting, e.g., 'How many patients with fever did I see this month?' \nor 'Find all patients mentioning back pain'.\n:param doctor_id: The UUID of the doctor.\n:param symptom_keyword: The keyword to search for in symptoms (e.g., 'fever', 'cough').\n:param start_date_str: The start date in YYYY-MM-DD format.\n:param end_date_str: The end date in YYYY-MM-DD format.\nReturns a list of matching appointments with patient details.",
        inputSchema={
            'properties': {
                'doctor_id': {'type': 'string'},
                'symptom_keyword': {'type': 'string'},
                'start_date_str': {'type': 'string'},
                'end_date_str': {'type': 'string'}
            },
            'required': ['doctor_id', 'symptom_keyword', 'start_date_str', 'end_date_str'],
            'type': 'object'
        },
        outputSchema={
            'additionalProperties': True,
            'type': 'object'
        },
        icons=None,
        annotations=None,
        meta={'_fastmcp': {'tags': []}},
        execution=None
    ),
    Tool(
        name='send_summary_report_to_slack',
        title=None,
        description="Sends a summary, schedule, or patient report directly to a doctor's Slack.\nUse this ONLY when the user explicitly asks to 'send to slack', 'notify me', or 'push to slack'.\n:param doctor_id: The UUID of the doctor.\n:param content: The actual text/report to send.",
        inputSchema={
            'properties': {
                'doctor_id': {'type': 'string'},
                'content': {'type': 'string'}
            },
            'required': ['doctor_id', 'content'],
            'type': 'object'
        },
        outputSchema={
            'additionalProperties': True,
            'type': 'object'
        },
        icons=None,
        annotations=None,
        meta={'_fastmcp': {'tags': []}},
        execution=None
    )
]

