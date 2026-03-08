import streamlit as st


# -------------------------------
# Editable template data
# -------------------------------
students_data = [
    {
        "name": "Student Name 1",
        "program": "PhD, Computer Science (Year 3)",
        "topic": "Research topic or project focus",
    },
    {
        "name": "Student Name 2",
        "program": "MS, Data Science (Year 1)",
        "topic": "Research topic or project focus",
    },
]

publications_data = [
    {
        "title": "Sample Publication Title",
        "authors": "Your Name, Coauthor A, Coauthor B",
        "venue": "Conference/Journal Name",
        "year": 2025,
        "link": "https://example.com/publication-1",
    },
    {
        "title": "Another Publication Title",
        "authors": "Your Name, Coauthor C",
        "venue": "Conference/Journal Name",
        "year": 2023,
        "link": "",
    },
]


def show_home() -> None:
    """Render the homepage section."""
    st.title("Your Name")
    st.subheader("Assistant Professor, Department Name")
    st.write("University Name")

    st.write(
        "Welcome to my academic homepage. "
        "I work on research in [your area], and I enjoy collaborating with students "
        "and researchers across disciplines."
    )

    st.markdown("### Quick Links")
    st.markdown("- Email: yourname@university.edu")
    st.markdown("- CV: [Download CV](https://example.com/cv)")
    st.markdown("- Google Scholar: [Profile](https://scholar.google.com)")


def show_bio() -> None:
    """Render the bio section."""
    st.title("Bio")

    st.write(
        "I am a faculty member in the Department of [Department Name] at [University]. "
        "My research interests include [Interest 1], [Interest 2], and [Interest 3]."
    )

    st.markdown("### Research Interests")
    st.markdown("- Interest 1")
    st.markdown("- Interest 2")
    st.markdown("- Interest 3")

    st.markdown("### Education")
    st.markdown("- PhD in [Field], [University], [Year]")
    st.markdown("- MS in [Field], [University], [Year]")
    st.markdown("- BS in [Field], [University], [Year]")

    st.markdown("### Experience")
    st.markdown("- [Current Position], [Institution], [Years]")
    st.markdown("- [Previous Position], [Institution], [Years]")


def show_students() -> None:
    """Render the students section from students_data."""
    st.title("Students")

    if not students_data:
        st.info("No student entries yet. Add dictionaries to students_data in main.py.")
        return

    for student in students_data:
        name = student.get("name", "Unknown Student")
        program = student.get("program", "Program not listed")
        topic = student.get("topic", "Topic not listed")

        st.markdown(f"### {name}")
        st.write(f"**Program:** {program}")
        st.write(f"**Topic/Role:** {topic}")
        st.write("")


def sort_publications_by_year_desc(publications: list[dict]) -> list[dict]:
    """Return publications sorted by year (newest first)."""

    # Use -1 for missing/invalid year so those entries appear at the end.
    def year_value(item: dict) -> int:
        year = item.get("year")
        return year if isinstance(year, int) else -1

    return sorted(publications, key=year_value, reverse=True)


def show_publications() -> None:
    """Render the publications section from publications_data."""
    st.title("Publications")

    if not publications_data:
        st.info("No publications yet. Add dictionaries to publications_data in main.py.")
        return

    sorted_publications = sort_publications_by_year_desc(publications_data)

    for publication in sorted_publications:
        title = publication.get("title", "Untitled")
        authors = publication.get("authors", "Authors not listed")
        venue = publication.get("venue", "Venue not listed")
        year = publication.get("year", "Year not listed")
        link = publication.get("link", "")

        st.markdown(f"### {title}")
        st.write(f"**Authors:** {authors}")
        st.write(f"**Venue:** {venue}")
        st.write(f"**Year:** {year}")

        if link:
            st.markdown(f"[Read publication]({link})")

        st.write("")


def main() -> None:
    """Set up page and route to selected section."""
    st.set_page_config(page_title="Academic Homepage", layout="wide")

    st.sidebar.title("Navigation")
    section = st.sidebar.radio(
        "Go to",
        ["Home", "Bio", "Students", "Publications"],
    )

    if section == "Home":
        show_home()
    elif section == "Bio":
        show_bio()
    elif section == "Students":
        show_students()
    elif section == "Publications":
        show_publications()


if __name__ == "__main__":
    main()
