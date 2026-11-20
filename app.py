import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------
st.set_page_config(
    page_title="RUPP Space",
    page_icon=":material/eco:",
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


def has_booking_conflict(
    room_name, booking_date, start_time, end_time,
    exclude_booking_id=None
):
    """Return True if the selected room has an overlapping booking."""
    new_start = datetime.combine(booking_date, start_time)
    new_end = datetime.combine(booking_date, end_time)

    for booking in st.session_state["bookings"]:
        if booking["Booking ID"] == exclude_booking_id:
            continue
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

def display_booking_card(booking):
    with st.container(border=True):

        st.caption(f"RESERVATION #{booking['Booking ID']:03d}")
        st.subheader(booking["Room"])

        room_info = get_room_data(booking["Room"])

        if room_info:
            st.caption(
                f":material/location_on: {room_info['Location']}"
            )

        col1, col2 = st.columns(2)

        with col1:
            st.caption("Date")
            st.write(booking["Date"].strftime("%d %B %Y"))

            st.caption("Number of people")
            st.write(f"{booking['People']} people")

        with col2:
            st.caption("Time")
            st.write(
                f"{booking['Start Time'].strftime('%H:%M')} - "
                f"{booking['End Time'].strftime('%H:%M')}"
            )

            st.caption("Purpose")
            st.write(booking["Purpose"])

        st.divider()

        if booking["Status"] == "Cancelled":
            st.caption(":material/cancel: Cancelled")

        elif datetime.combine(
            booking["Date"], booking["End Time"]
        ) <= datetime.now():
            st.caption(":material/check_circle: Completed")

        else:
            st.success(
                "Confirmed",
                icon=":material/check_circle:"
            )

            if datetime.combine(
                booking["Date"], booking["Start Time"]
            ) > datetime.now():

                action_col1, action_col2 = st.columns(2)

                with action_col1:
                    if st.button(
                        "Reschedule",
                        key=f"reschedule_{booking['Booking ID']}",
                        use_container_width=True
                    ):
                        st.session_state["pending_reschedule"] = booking["Booking ID"]

                with action_col2:
                    if st.button(
                        "Cancel booking",
                        key=f"cancel_{booking['Booking ID']}",
                        use_container_width=True
                    ):
                        st.session_state["pending_cancel"] = booking["Booking ID"]
# Rescheduling form
                if st.session_state.get("pending_reschedule") == booking["Booking ID"]:

                    st.markdown("**Reschedule your reservation**")

                    with st.form(
                        key=f"reschedule_form_{booking['Booking ID']}"
                    ):
                        new_date = st.date_input(
                            "New booking date",
                            value=booking["Date"],
                            min_value=date.today()
                        )

                        time_col1, time_col2 = st.columns(2)

                        with time_col1:
                            new_start = st.time_input(
                                "Start time",
                                value=booking["Start Time"]
                            )

                        with time_col2:
                            new_end = st.time_input(
                                "End time",
                                value=booking["End Time"]
                            )

                        save_col, close_col = st.columns(2)

                        with save_col:
                            save_changes = st.form_submit_button(
                                "Save changes",
                                type="primary",
                                use_container_width=True
                            )

                        with close_col:
                            close_form = st.form_submit_button(
                                "Go back",
                                use_container_width=True
                            )

                    if close_form:
                        st.session_state["pending_reschedule"] = None
                        st.rerun()

                    if save_changes:

                        if new_start >= new_end:
                            st.warning(
                                "End time must be later than start time."
                            )

                        elif datetime.combine(
                            new_date, new_start
                        ) < datetime.now():
                            st.warning(
                                "Please select a future date and time."
                            )

                        elif has_booking_conflict(
                            booking["Room"],
                            new_date,
                            new_start,
                            new_end,
                            exclude_booking_id=booking["Booking ID"]
                        ):
                            st.error(
                                "This room is already booked during "
                                "the selected time. Please choose another time."
                            )

                        else:
                            booking["Date"] = new_date
                            booking["Start Time"] = new_start
                            booking["End Time"] = new_end

                            st.session_state["pending_reschedule"] = None
                            st.session_state["booking_message"] = "Reservation successfully rescheduled!"
                            st.rerun()

                if st.session_state.get("pending_cancel") == booking["Booking ID"]:

                    st.warning("Are you sure you want to cancel this reservation?")

                    confirm_col, back_col = st.columns(2)

                    with confirm_col:
                        if st.button(
                            "Yes, cancel",
                            key=f"confirm_{booking['Booking ID']}",
                            use_container_width=True
                        ):
                            booking["Status"] = "Cancelled"
                            st.session_state["pending_cancel"] = None
                            st.session_state["booking_message"] = "Reservation successfully cancelled."
                            st.rerun()

                    with back_col:
                        if st.button(
                            "Keep reservation",
                            key=f"keep_{booking['Booking ID']}",
                            use_container_width=True
                        ):
                            st.session_state["pending_cancel"] = None
                            st.rerun()
def reserve_room(room_name):
    st.session_state["selected_room_name"] = room_name
    st.session_state["navigation"] = "Book a Room"

def navigate_to(page):
    st.session_state["navigation"] = page

def is_room_occupied(room_name):
    current_time = datetime.now()

    for booking in st.session_state["bookings"]:

        if booking["Room"] != room_name:
            continue

        if booking["Status"] != "Booked":
            continue

        booking_start = datetime.combine(
            booking["Date"], booking["Start Time"]
        )

        booking_end = datetime.combine(
            booking["Date"], booking["End Time"]
        )

        if booking_start <= current_time < booking_end:
            return True

    return False



# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
# SIDEBAR NAVIGATION
with st.sidebar:
    st.header(":material/eco: RUPP Space")
    st.caption("University room booking system")

    st.divider()
    st.caption("MENU")

    selected_page = st.radio(
        "MENU",
        ["Home", "Book a Room", "My Bookings",
         "Room Directory", "About"],
        label_visibility="collapsed",
        format_func=lambda page: {
            "Home": ":material/home: Home",
            "Book a Room": ":material/calendar_add_on: Book a Room",
            "My Bookings": ":material/bookmark: My Bookings",
            "Room Directory": ":material/search: Room Directory",
            "About": ":material/info: About"
        }[page],
        key="navigation"
    )

    st.divider()

    st.caption("Royal University of Phnom Penh")
    st.caption("Room Booking · 2026")

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
if selected_page == "Home":
    st.title("Find your study space.")
    st.write(
        "Discover and reserve university spaces for studying, "
        "meetings and collaborative learning."
    )

# Metric calculations
    total_rooms = len(ROOMS)
    total_bookings = len(st.session_state["bookings"])
    active_bookings = sum(
        1 for booking in st.session_state["bookings"]
        if booking["Status"] == "Booked"
    )

# Metric cards
    st.subheader("Booking overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric("Listed rooms", total_rooms)

    with col2:
        with st.container(border=True):
            st.metric("Total bookings", total_bookings)

    with col3:
        with st.container(border=True):
            st.metric("Active bookings", active_bookings)
    st.divider()
    st.subheader("Quick actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button(
            ":material/calendar_add_on: Book a Room",
            use_container_width=True,
            type="primary",
            on_click=navigate_to,
            args=("Book a Room",)
        )

    with col2:
        st.button(
            ":material/search: Explore Rooms",
            use_container_width=True,
            on_click=navigate_to,
            args=("Room Directory",)
        )

    with col3:
        st.button(
            ":material/bookmark: My Bookings",
            use_container_width=True,
            on_click=navigate_to,
            args=("My Bookings",)
        )

 
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

    st.title("Reserve your space.")
    st.write(
        "Choose a room and schedule your next study session."
    )

    st.divider()

    # Room selection
    room_names = [room["Room"] for room in ROOMS]
    room_name = st.selectbox(
        "Select a Room",
        room_names,
        key="selected_room_name"
    )
    # Display selected room information
    selected_room = get_room_data(room_name)

    if selected_room:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.caption("Location")
                st.write(selected_room["Location"])

            with col2:
                st.caption("Room type")
                st.write(selected_room["Type"])

            with col3:
                st.caption("Capacity")
                st.write(f"{selected_room['Capacity']} people")

    recommended_capacity = selected_room["Capacity"] if selected_room else 1
    maximum_capacity = int(recommended_capacity*1.5)

    number_of_people = st.number_input(
        "Number of People",
        min_value=1,
        max_value=100,
        value=2
    )

    if number_of_people > maximum_capacity:
        st.error(
            f"This room cannot accommodate more than {maximum_capacity} people. "
            "Please select a larger room.",
            icon=":material/error:"
        )

    elif number_of_people > recommended_capacity:
        st.warning(
            f"The recommended capacity is {recommended_capacity} people. "
            "The room may feel crowded or uncomfortable.",
            icon=":material/warning:"
        )

    # Booking form
    with st.form("booking_form"):
        student_name = st.text_input("Student Name")
        student_id = st.text_input("Student ID")

        booking_date = st.date_input(
            "Booking Date",
            min_value=date.today()
        )

        col1, col2 = st.columns(2)

        with col1:
            start_time = st.time_input(
                "Start Time", value=time(9, 0)
            )

        with col2:
            end_time = st.time_input(
                "End Time", value=time(10, 0)
            )


        purpose = st.selectbox(
            "Purpose",
            [
                "Individual Study",
                "Group Study",
                "Meeting",
                "Discussion",
                "Other"
            ]
        )

        submitted = st.form_submit_button(
            "Confirm reservation",
            type="primary",
            use_container_width=True,
            disabled=number_of_people > maximum_capacity
        )

    # Booking validation
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

        elif datetime.combine(booking_date, start_time) < datetime.now():
            st.warning("Please select a start time that has not already passed.")

        elif number_of_people > maximum_capacity:
            st.error(
            f"This room cannot accommodate more than "
            f"{maximum_capacity} people."
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

            st.success(
                "Your reservation is confirmed!",
                icon=":material/check_circle:"
            )

            with st.container(border=True):
                st.subheader("Reservation summary")
                st.caption(f"Booking ID: #{new_booking['Booking ID']}")

                st.markdown(f"**{room_name}**")

                col1, col2 = st.columns(2)

                with col1:
                    st.caption("Date")
                    st.write(booking_date.strftime("%d %B %Y"))

                    st.caption("Number of people")
                    st.write(number_of_people)

                with col2:
                    st.caption("Time")
                    st.write(
                        f"{start_time.strftime('%H:%M')} - "
                        f"{end_time.strftime('%H:%M')}"
                    )

                    st.caption("Purpose")
                    st.write(purpose)

                st.divider()
                st.caption(f"Reserved by {student_name.strip()}")

# ---------------------------------------------------------
# MY BOOKINGS PAGE
# ---------------------------------------------------------
elif selected_page == "My Bookings":
    st.title("My Bookings")
    st.write("View and manage your room reservations.")

    if "booking_message" in st.session_state:
        st.toast(
            st.session_state["booking_message"],
            icon=":material/check_circle:"
        )
        del st.session_state["booking_message"]

    bookings_df = get_bookings_dataframe()

    upcoming = []
    past = []
    cancelled = []

    for booking in st.session_state["bookings"]:
        booking_end = datetime.combine(
            booking["Date"], booking["End Time"]
        )

        if booking["Status"] == "Cancelled":
            cancelled.append(booking)

        elif booking_end <= datetime.now():
            past.append(booking)

        else:
            upcoming.append(booking)

    tab1, tab2, tab3 = st.tabs([
        f"Upcoming ({len(upcoming)})",
        f"Past bookings ({len(past)})",
        f"Cancelled ({len(cancelled)})"
    ])

    with tab1:
        if not upcoming:
            st.info("You have no upcoming reservations.")
        else:
            for booking in upcoming:
                display_booking_card(booking)

    with tab2:
        if not past:
            st.info("Your past reservations will appear here.")
        else:
            for booking in past:
                display_booking_card(booking)

    with tab3:
        if not cancelled:
            st.info("You have no cancelled reservations.")
        else:
            for booking in cancelled:
                display_booking_card(booking)



# ---------------------------------------------------------
# ROOM DIRECTORY PAGE
# ---------------------------------------------------------
elif selected_page == "Room Directory":
    st.title("Room Directory")
    st.write("Explore university spaces and find the right room for your needs.")

    st.divider()

    rooms_df = pd.DataFrame(ROOMS)

    search_query = st.text_input(
        "Search rooms",
        placeholder="Search by room name..."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        location_options = ["All"] + sorted(
            rooms_df["Location"].unique().tolist()
        )

        selected_location = st.selectbox(
            "Location", location_options
        )

    with col2:
        type_options = ["All"] + sorted(
            rooms_df["Type"].unique().tolist()
        )

        selected_type = st.selectbox(
            "Room type", type_options
        )

    with col3:
        required_capacity = st.number_input(
            "Group size",
            min_value=1,
            max_value=100,
            value=1
        )

    filtered_rooms = rooms_df.copy()

    if search_query.strip():
        filtered_rooms = filtered_rooms[
            filtered_rooms["Room"].str.contains(
                search_query.strip(),
                case=False,
                regex=False
            )
        ]

    if selected_location != "All":
        filtered_rooms = filtered_rooms[
            filtered_rooms["Location"] == selected_location
        ]

    if selected_type != "All":
        filtered_rooms = filtered_rooms[
            filtered_rooms["Type"] == selected_type
        ]

    filtered_rooms = filtered_rooms[
        filtered_rooms["Capacity"] >= required_capacity
    ]

    st.caption(f"{len(filtered_rooms)} rooms found")

    if filtered_rooms.empty:
        st.info("No rooms match your selected filters.")

    else:
        columns = st.columns(2)

        for index, (_, room) in enumerate(filtered_rooms.iterrows()):

            with columns[index % 2]:
                with st.container(border=True):

                    room_icons = {
                        "Study Room": ":material/menu_book:",
                        "Meeting Room": ":material/groups:",
                        "Computer Room": ":material/computer:"
                    }

                    room_icon = room_icons.get(
                        room["Type"], ":material/meeting_room:"
                    )

                    icon_col, space_col, status_col = st.columns(
                        [1, 4, 2],
                        vertical_alignment="center"
                    )

                    with icon_col:
                        st.subheader(room_icon)

                    with status_col:
                        if is_room_occupied(room["Room"]):
                            st.markdown(":orange[:material/circle: Occupied now]")
                        else:
                            st.markdown(":green[:material/circle: Available now]")

                    st.markdown(f"**{room['Room']}**")

                    st.caption(
                        f":material/location_on: {room['Location']}"
                    )

                    st.write(room["Type"])

                    st.divider()

                    st.write(
                        f":material/group: {room['Capacity']} people"
                    )
                    st.button(
                        "Reserve room",
                        key=f"reserve_{room['Room']}",
                        type="primary",
                        use_container_width=True,
                        on_click=reserve_room,
                        args=(room["Room"],)
                    )
    st.caption(
        "The room names and capacities are sample data. Replace them with "
        "verified room information before using this system officially."
    )

# ---------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------
# ---------------------------------------------------------
# ABOUT PAGE
# ---------------------------------------------------------
else:
    st.title("About RUPP Space")
    st.write("Making university spaces easier to discover and reserve.")

    st.divider()

    st.subheader("Main features")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("**:material/search: Discover spaces**")
            st.write("Explore rooms by location, type and capacity.")

        with st.container(border=True):
            st.markdown("**:material/calendar_add_on: Reserve rooms**")
            st.write("Schedule reservations with automatic conflict checking.")

    with col2:
        with st.container(border=True):
            st.markdown("**:material/bookmark: Manage bookings**")
            st.write("View, reschedule and cancel your reservations.")

        with st.container(border=True):
            st.markdown("**:material/groups: Plan together**")
            st.write("Find suitable spaces for individual and group activities.")

    st.divider()

    st.subheader("About the project")

    st.write("**University:** Royal University of Phnom Penh")
    st.write("**Course:** Web Application Development")
    st.write("**Technology:** Python, Streamlit and Pandas")

    st.info(
        "RUPP Space is a prototype, not an official university "
        "booking service. Room information is sample data, and reservations "
        "are stored temporarily during the current session.",
        icon=":material/info:"
    )

    st.caption("RUPP Space · Web Application Development · 2026")
