# RUPP Room Booking System

A simple Streamlit web application prototype for booking university spaces at the Royal University of Phnom Penh (RUPP).

Students can use the prototype to view sample rooms, submit bookings, check for time conflicts, view booking records, and cancel bookings.

## Features

- Home page with booking summary
- Room directory with location filter
- Booking form
- Validation for required fields, date, time, and room capacity
- Conflict checking to prevent overlapping bookings for the same room
- View and cancel bookings
- About page

## Project files

```text
rupp_room_booking_app/
├── app.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.9 or newer
- Streamlit
- Pandas
- A web browser

## Installation

1. Open the project folder in VS Code.
2. Open the terminal.
3. (Optional but recommended) Create a virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment.

   **Windows PowerShell:**
   ```powershell
   .\\venv\\Scripts\\Activate.ps1
   ```

   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

5. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Run the application

In the terminal, run:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, usually `http://localhost:8501`. Open it in your browser.

## How to use

1. Select **Room Directory** to view the sample rooms.
2. Select **Book a Room**.
3. Enter the student details, room, date, time, number of people, and purpose.
4. Submit the form. The app checks the information and looks for an overlapping booking.
5. Select **My Bookings** to see booking records or cancel an active booking.

## Important notes and limitations

- Room names, locations, and capacities are sample data for demonstration. They are not verified official RUPP room information.
- Booking records are stored in Streamlit session state. They are temporary and may be lost when the app session restarts.
- This version does not have a login system, permanent database, email notification, or administrator approval workflow.
- This is a classroom prototype, not an official RUPP reservation service.

## Possible future improvements

- Connect the application to SQLite or PostgreSQL.
- Add student and administrator login.
- Allow an administrator to add, edit, or remove rooms.
- Add a calendar view.
- Add booking approval and email notifications.
