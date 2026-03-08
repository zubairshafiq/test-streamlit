import html
import re
from urllib.error import URLError
from urllib.request import urlopen

import streamlit as st


HOME_URL = "https://web.cs.ucdavis.edu/~zubair/"
BIO_URL = "https://web.cs.ucdavis.edu/~zubair/bio.html"
STUDENTS_URL = "https://web.cs.ucdavis.edu/~zubair/students.html"
PUBLICATIONS_URL = "https://web.cs.ucdavis.edu/~zubair/pubs.html"


def fetch_html(url: str) -> str:
    """Download HTML content from a URL and return it as text."""
    with urlopen(url, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_layout_content(page_html: str) -> str:
    """Extract only the main content block from the jemdoc page."""
    match = re.search(r'<td id="layout-content">(.*?)</td>', page_html, re.DOTALL)
    return match.group(1) if match else ""


def remove_tags(text: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = text.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)

    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def parse_home_data(page_html: str) -> dict:
    """Parse the homepage title, profile summary, interests, and recent publications."""
    content = extract_layout_content(page_html)

    name_match = re.search(r"<h1>(.*?)</h1>", content, re.DOTALL)
    name = remove_tags(name_match.group(1)) if name_match else "Zubair Shafiq"

    # Grab the first profile paragraph under the image.
    profile_match = re.search(r"<p>(Professor.*?)</p>", content, re.DOTALL)
    profile_text = remove_tags(profile_match.group(1)) if profile_match else ""

    interest_match = re.search(
        r"<h2>Research Interests</h2>\s*<p>(.*?)</p>",
        content,
        re.DOTALL,
    )
    interest_text = remove_tags(interest_match.group(1)) if interest_match else ""

    recent_pubs_section_match = re.search(
        r"<h2>Recent Publications</h2>(.*)",
        content,
        re.DOTALL,
    )
    recent_pubs_section = recent_pubs_section_match.group(1) if recent_pubs_section_match else ""

    recent_items = re.findall(r"<li><p>(.*?)</p>\s*</li>", recent_pubs_section, re.DOTALL)

    recent_publications = []
    for item in recent_items:
        title_match = re.search(r"<b>(.*?)</b>", item, re.DOTALL)
        title = remove_tags(title_match.group(1)) if title_match else "Untitled"

        venue_text = remove_tags(item)
        lines = venue_text.split("\n")
        venue_line = lines[1] if len(lines) > 1 else ""

        link_match = re.search(r'href="([^"]+)"', item)
        link = link_match.group(1) if link_match else ""

        recent_publications.append(
            {
                "title": title,
                "venue": venue_line,
                "link": link,
            }
        )

    return {
        "name": name,
        "profile_text": profile_text,
        "interest_text": interest_text,
        "recent_publications": recent_publications,
    }


def parse_bio_data(page_html: str) -> str:
    """Parse the biography paragraph from the bio page."""
    content = extract_layout_content(page_html)
    paragraphs = re.findall(r"<p>(.*?)</p>", content, re.DOTALL)

    cleaned_paragraphs = [remove_tags(p) for p in paragraphs]
    cleaned_paragraphs = [p for p in cleaned_paragraphs if p and p != "<br />"]

    return "\n\n".join(cleaned_paragraphs)


def parse_students_data(page_html: str) -> dict[str, list[str]]:
    """Parse students page into section header -> entries."""
    content = extract_layout_content(page_html)

    # Split into sections like Doctorate, Masters, Undergraduate, etc.
    section_pattern = r"<h1>(.*?)</h1>(.*?)(?=<h1>|$)"
    sections = re.findall(section_pattern, content, re.DOTALL)

    students_by_section: dict[str, list[str]] = {}
    for section_title_html, section_body in sections:
        section_title = remove_tags(section_title_html)
        items = re.findall(r"<li><p>(.*?)</p>\s*</li>", section_body, re.DOTALL)

        cleaned_items = [remove_tags(item) for item in items]
        cleaned_items = [item for item in cleaned_items if item]

        students_by_section[section_title] = cleaned_items

    return students_by_section


def parse_publications_data(page_html: str) -> list[dict]:
    """Parse publication entries into dictionaries for clean rendering."""
    content = extract_layout_content(page_html)
    items = re.findall(r"<li><p>(.*?)</p>\s*</li>", content, re.DOTALL)

    publications_data = []
    for item in items:
        title_match = re.search(r"<b>(.*?)</b>", item, re.DOTALL)
        title = remove_tags(title_match.group(1)) if title_match else "Untitled"

        text_block = remove_tags(item)
        lines = text_block.split("\n")

        authors = lines[1] if len(lines) > 1 else "Authors not listed"
        venue = lines[2] if len(lines) > 2 else "Venue not listed"

        year_match = re.search(r"(19|20)\d{2}", venue)
        year = int(year_match.group(0)) if year_match else None

        link_match = re.search(r'href="([^"]+)"', item)
        link = link_match.group(1) if link_match else ""

        publications_data.append(
            {
                "title": title,
                "authors": authors,
                "venue": venue,
                "year": year,
                "link": link,
            }
        )

    return publications_data


@st.cache_data(ttl=3600)
def load_site_content() -> dict:
    """Fetch and parse all content pages. Cache results for one hour."""
    home_html = fetch_html(HOME_URL)
    bio_html = fetch_html(BIO_URL)
    students_html = fetch_html(STUDENTS_URL)
    publications_html = fetch_html(PUBLICATIONS_URL)

    return {
        "home": parse_home_data(home_html),
        "bio": parse_bio_data(bio_html),
        "students": parse_students_data(students_html),
        "publications": parse_publications_data(publications_html),
    }


def show_home(home_data: dict) -> None:
    st.title(home_data.get("name", "Zubair Shafiq"))

    profile_text = home_data.get("profile_text", "")
    if profile_text:
        st.write(profile_text)

    interest_text = home_data.get("interest_text", "")
    if interest_text:
        st.markdown("### Research Interests")
        st.write(interest_text)

    recent_publications = home_data.get("recent_publications", [])
    if recent_publications:
        st.markdown("### Recent Publications")
        for pub in recent_publications:
            st.markdown(f"**{pub['title']}**")
            if pub["venue"]:
                st.write(pub["venue"])
            if pub["link"]:
                st.markdown(f"[Read/Download]({pub['link']})")
            st.write("")


def show_bio(bio_text: str) -> None:
    st.title("Bio")
    st.write(bio_text)


def show_students(students_by_section: dict[str, list[str]]) -> None:
    st.title("Students")

    if not students_by_section:
        st.info("Could not load students data right now.")
        return

    for section_title, entries in students_by_section.items():
        st.markdown(f"### {section_title}")
        for entry in entries:
            # Render each entry as a multiline block for readability.
            st.markdown(f"- {entry.replace(chr(10), '<br>')}", unsafe_allow_html=True)


def sort_publications_by_year_desc(publications: list[dict]) -> list[dict]:
    def year_value(item: dict) -> int:
        year = item.get("year")
        return year if isinstance(year, int) else -1

    return sorted(publications, key=year_value, reverse=True)


def show_publications(publications_data: list[dict]) -> None:
    st.title("Publications")

    if not publications_data:
        st.info("Could not load publications data right now.")
        return

    for publication in sort_publications_by_year_desc(publications_data):
        st.markdown(f"### {publication.get('title', 'Untitled')}")
        st.write(f"**Authors:** {publication.get('authors', 'Authors not listed')}")
        st.write(f"**Venue:** {publication.get('venue', 'Venue not listed')}")

        year = publication.get("year")
        st.write(f"**Year:** {year if year is not None else 'Not listed'}")

        link = publication.get("link", "")
        if link:
            st.markdown(f"[Read publication]({link})")

        st.write("")


def main() -> None:
    st.set_page_config(page_title="Zubair Shafiq", layout="wide")

    st.sidebar.title("Navigation")
    section = st.sidebar.radio("Go to", ["Home", "Bio", "Students", "Publications"])

    try:
        site_content = load_site_content()
    except URLError:
        st.error("Could not fetch remote website content. Please check your internet connection.")
        return
    except Exception:
        st.error("An unexpected error happened while loading website content.")
        return

    if section == "Home":
        show_home(site_content["home"])
    elif section == "Bio":
        show_bio(site_content["bio"])
    elif section == "Students":
        show_students(site_content["students"])
    elif section == "Publications":
        show_publications(site_content["publications"])


if __name__ == "__main__":
    main()
