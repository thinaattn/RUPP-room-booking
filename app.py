import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------
st.set_page_config(
    page_title="RUPP Room Booking",
    page_icon="🏫",
    layout="wide"
)

# ---------------------------------------------------------
# SAMPLE ROOM INFORMATION
# Edit this list to match the rooms your project will use.
# These are sample rooms, not confirmed official RUPP rooms.
# ---------------------------------------------------------
ROOMS = [
    {
        "Room": "Library Study Room 1",
        "Location": "Library",
        "Capacity": 6,
        "Type": "Study Room"
    },
    {
        "Room": "Library Study Room 2",
        "Location": "Library",
        "Capacity": 8,
        "Type": "Study Room"
    },
    {
        "Room": "Meeting Room A",
        "Location": "Main Building",
        "Capacity": 10,
        "Type": "Meeting Room"
    },
    {
        "Room": "Meeting Room B",
        "Location": "Main Building",
        "Capacity": 15,
        "Type": "Meeting Room"
    },
    {
        "Room": "Computer Lab 1",
        "Location": "Computer Building",
        "Capacity": 25,
        "Type": "Computer Room"
    }
]

# ---------------------------------------------------------
# SESSION STATE
# Bookings are stored during the current app session.
# They will reset when the app session restarts.
# ---------------------------------------------------------
if "bookings" not in st.session_state:
    st.session_state["bookings"] = []

# ---------------------------------------------------------
# HELPER FUNCTIONS heelp
# ---------------------------------------------------------
def get_room_data(room_name):
    for room in ROOMS:
        if room["Room"] == room_name:
            return room
    return None


def has_booking_conflict(room_name, booking_date, start_time, end_time):
    """Return True if the selected room has an overlapping booking."""
    new_start = datetime.combine(booking_date, start_time)
    new_end = datetime.combine(booking_date, end_time)

    for booking in st.session_state["bookings"]:
        if booking["Room"] != room_name:
            continue

        if booking["Date"] != booking_date:
            continue

        if booking["Status"] != "Booked":
            continue

        old_start = datetime.combine(booking["Date"], booking["Start Time"])
        old_end = datetime.combine(booking["Date"], booking["End Time"])

        # Two time periods overlap when each starts before the other ends.
        if new_start < old_end and old_start < new_end:
            return True

    return False


def get_bookings_dataframe():
    if len(st.session_state["bookings"]) == 0:
        return pd.DataFrame()

    return pd.DataFrame(st.session_state["bookings"])


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.title("🏫 RUPP Room Booking")
    st.caption("University room reservation system")
    selected_page = st.radio(
        "Navigation",
        ["Home", "Book a Room", "My Bookings", "Room Directory", "About"]
    )

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
if selected_page == "Home":
    st.title("RUPP Room Booking System")
    st.subheader("Book a study room, meeting room, or university space.")
    st.write(
        "This simple web application helps students reserve available "
        "university rooms for studying, group discussions, and meetings."
    )

    total_rooms = len(ROOMS)
    total_bookings = len(st.session_state["bookings"])
    active_bookings = sum(
        1 for booking in st.session_state["bookings"]
        if booking["Status"] == "Booked"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Rooms Listed", total_rooms)
    col2.metric("Total Booking Records", total_bookings)
    col3.metric("Active Bookings", active_bookings)

    st.divider()
    st.subheader("How to use the system")
    st.markdown(
        """
        1. Open **Room Directory** to see the sample rooms.
        2. Select **Book a Room** and enter your booking information.
        3. The system checks whether the room is already booked at that time.
        4. Open **My Bookings** to view or cancel your bookings.
        """
    )

    st.info(
        "Note: This is a classroom prototype. Booking records are stored "
        "temporarily in the current Streamlit session."
    )

# ---------------------------------------------------------
# BOOK A ROOM PAGE
# ---------------------------------------------------------
elif selected_page == "Book a Room":
    st.title("Book a Room")
    st.write("Complete the form below to request a room reservation.")

    room_names = [room["Room"] for room in ROOMS]

    with st.form("booking_form"):
        student_name = st.text_input("Student Name")
        student_id = st.text_input("Student ID")
        room_name = st.selectbox("Select a Room", room_names)
        booking_date = st.date_input(
            "Booking Date",
            min_value=date.today()
        )

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", value=time(9, 0))
        with col2:
            end_time = st.time_input("End Time", value=time(10, 0))

        number_of_people = st.number_input(
            "Number of People",
            min_value=1,
            max_value=100,
            value=2
        )
        purpose = st.selectbox(
            "Purpose",
            ["Individual Study", "Group Study", "Meeting", "Discussion", "Other"]
        )

        submitted = st.form_submit_button("Submit Booking", use_container_width=True)

    if submitted:
        room_info = get_room_data(room_name)

        if student_name.strip() == "":
            st.warning("Please enter your name.")
        elif student_id.strip() == "":
            st.warning("Please enter your student ID.")
        elif start_time >= end_time:
            st.warning("End time must be later than start time.")
        elif booking_date < date.today():
            st.warning("Please select today or a future date.")
        elif room_info and number_of_people > room_info["Capacity"]:
            st.warning(
                f"This room has a capacity of {room_info['Capacity']} people. "
                "Please reduce the number of people or select another room."
            )
        elif has_booking_conflict(
            room_name, booking_date, start_time, end_time
        ):
            st.error(
                "This room is already booked during the selected time. "
                "Please choose another time or room."
            )
        else:
            new_booking = {
                "Booking ID": len(st.session_state["bookings"]) + 1,
                "Student Name": student_name.strip(),
                "Student ID": student_id.strip(),
                "Room": room_name,
                "Date": booking_date,
                "Start Time": start_time,
                "End Time": end_time,
                "People": int(number_of_people),
                "Purpose": purpose,
                "Status": "Booked"
            }

            st.session_state["bookings"].append(new_booking)
            st.success("Your room has been booked successfully!")
            st.write("Booking details:")
            st.write(f"**Booking ID:** {new_booking['Booking ID']}")
            st.write(f"**Room:** {room_name}")
            st.write(f"**Date:** {booking_date}")
            st.write(f"**Time:** {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

    selected_room = get_room_data(room_name)
    if selected_room:
        st.caption(
            f"Location: {selected_room['Location']} | "
            f"Type: {selected_room['Type']} | "
            f"Capacity: {selected_room['Capacity']} people"
        )

# ---------------------------------------------------------
# MY BOOKINGS PAGE
# ---------------------------------------------------------
elif selected_page == "My Bookings":
    st.title("My Bookings")
    st.write("View the booking records created during this app session.")

    bookings_df = get_bookings_dataframe()

    if bookings_df.empty:
        st.info("There are no bookings yet. Go to 'Book a Room' to create one.")
    else:
        st.dataframe(bookings_df, use_container_width=True, hide_index=True)

        st.subheader("Cancel a Booking")
        active_bookings = [
            booking for booking in st.session_state["bookings"]
            if booking["Status"] == "Booked"
        ]

        if active_bookings:
            booking_options = {
                f"ID {b['Booking ID']} - {b['Room']} - {b['Date']} "
                f"({b['Start Time'].strftime('%H:%M')})": b["Booking ID"]
                for b in active_bookings
            }

            selected_booking_label = st.selectbox(
                "Select a booking to cancel",
                list(booking_options.keys())
            )

            if st.button("Cancel Selected Booking"):
                selected_id = booking_options[selected_booking_label]

                for booking in st.session_state["bookings"]:
                    if booking["Booking ID"] == selected_id:
                        booking["Status"] = "Cancelled"
                        break

                st.success("Booking cancelled.")
                st.rerun()
        else:
            st.info("There are no active bookings to cancel.")

# ---------------------------------------------------------
# ROOM DIRECTORY PAGE
# ---------------------------------------------------------
elif selected_page == "Room Directory":
    st.title("Room Directory")
    st.write("Browse the sample rooms available in this prototype.")

    rooms_df = pd.DataFrame(ROOMS)

    location_options = ["All"] + sorted(rooms_df["Location"].unique().tolist())
    selected_location = st.selectbox("Filter by Location", location_options)

    filtered_rooms = rooms_df.copy()
    if selected_location != "All":
        filtered_rooms = filtered_rooms[
            filtered_rooms["Location"] == selected_location
        ]

    st.dataframe(filtered_rooms, use_container_width=True, hide_index=True)

    st.caption(
        "The room names and capacities are sample data. Replace them with "
        "verified room information before using this system officially."
    )

# ---------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------
else:
    st.title("About This Project")
    st.write("**Project:** RUPP Room Booking System")
    st.write("**Course:** Web Application Development")
    st.write("**Purpose:** A simple prototype for reserving university rooms.")

    st.markdown(
        """
        **Main features**
        - View a list of sample university rooms.
        - Submit a room booking request.
        - Check for overlapping bookings.
        - View booking records.
        - Cancel an active booking.
        - Filter rooms by location.

        **Technology**
        - Python
        - Streamlit
        - Pandas
        """
    )

    st.warning(
        "This is a learning prototype, not an official RUPP booking service. "
        "It does not connect to a university database or verify real room availability."
    )
