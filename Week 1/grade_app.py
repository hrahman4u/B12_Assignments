import streamlit as st


# Keep the same grading scale from Day 2
def get_grade(mark):
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "F"


# Keep students between Streamlit reruns
if "students" not in st.session_state:
    st.session_state.students = []


st.title("Student Grade Manager")

st.write("Add students and their marks below.")


# Form for adding a student
with st.form("student_form"):
    name = st.text_input("Name")
    mark = st.number_input(
        "Mark",
        min_value=0,
        max_value=100,
        value=0,
        step=1
    )

    submitted = st.form_submit_button("Add Student")

    if submitted:
        if not name.strip():
            st.error("Please enter a student name.")
        else:
            st.session_state.students.append({
                "name": name.strip(),
                "mark": mark,
                "grade": get_grade(mark)
            })

            st.success(f"{name.strip()} was added.")


# Display students and class statistics
if st.session_state.students:

    st.subheader("Students")

    for index, student in enumerate(st.session_state.students):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            st.write(student["name"])

        with col2:
            st.write(student["mark"])

        with col3:
            st.write(student["grade"])

        with col4:
            if st.button("Delete", key=f"delete_{index}"):
                st.session_state.students.pop(index)
                st.rerun()

    # Calculate class statistics
    marks = [
        student["mark"]
        for student in st.session_state.students
    ]

    if marks:
        average = sum(marks) / len(marks)
        highest = max(marks)
        lowest = min(marks)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Average", f"{average:.1f}")

        with col2:
            st.metric("Highest", highest)

        with col3:
            st.metric("Lowest", lowest)

else:
    st.info("No students have been added yet.")