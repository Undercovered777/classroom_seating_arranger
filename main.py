from js import document
from pyodide.ffi import create_proxy
import random

# Initialize student data
students = []
desks = []
dragged_student = None
dragged_desk = None
current_page = 1
desks_per_page = 40
teacher_view = False  # Default: Normal view

def generate_seating(event=None):
    global students, desks, current_page
    textarea = document.getElementById("studentList")
    student_text = textarea.value.strip()
    
    if not student_text:
        document.getElementById("status").innerHTML = "Please enter student names"
        return
        
    students = [name.strip() for name in student_text.split('\n') if name.strip()]
    document.getElementById("status").innerHTML = f"Loaded {len(students)} students"
    
    # Clear previous desks
    classroom = document.getElementById("classroom")
    classroom.innerHTML = ""
    
    # Create desks based on number of students (with some extra)
    total_desks = max(len(students), 24)  # At least 24 desks
    desks.clear()
    
    col_count = 6  # 6 desks per row, with spacers after col 2 and col 4
    
    for i in range(total_desks):
        col_index = (i % col_count) + 1
        
        # Insert spacer after 2nd and 4th columns
        if col_index == 3 or col_index == 5:
            spacer = document.createElement("div")
            spacer.className = "spacer"
            classroom.appendChild(spacer)
        
        desk = document.createElement("div")
        desk.className = "desk empty"
        desk.id = f"desk-{i}"
        desk.setAttribute("data-student", "")
        desk.setAttribute("data-desk-id", i)
        
        # Apply current view rotation
        desk.style.transform = "rotate(180deg)" if teacher_view else "rotate(0deg)"
        
        # Add drag and drop event listeners
        desk.addEventListener("dragover", create_proxy(allow_drop))
        desk.addEventListener("drop", create_proxy(drop))
        
        classroom.appendChild(desk)
        desks.append(desk)
    
    # Create pagination if needed
    setup_pagination()
    
    # Arrange students randomly initially
    arrange_random()

def setup_pagination():
    pagination_div = document.getElementById("pagination")
    pagination_div.innerHTML = ""
    
    total_pages = (len(desks) + desks_per_page - 1) // desks_per_page
    
    if total_pages <= 1:
        document.getElementById("page-info").textContent = ""
        return
        
    for i in range(total_pages):
        page_btn = document.createElement("button")
        page_btn.textContent = f"Page {i+1}"
        page_btn.addEventListener("click", create_proxy(lambda e, page=i+1: show_page(page)))
        if i == 0:
            page_btn.classList.add("active")
        pagination_div.appendChild(page_btn)
    
    document.getElementById("page-info").textContent = f"(Page 1 of {total_pages})"

def show_page(page):
    global current_page
    current_page = page
    
    # Update active button
    buttons = document.querySelectorAll("#pagination button")
    for i, btn in enumerate(buttons):
        if i+1 == page:
            btn.classList.add("active")
        else:
            btn.classList.remove("active")
    
    # Show desks for this page
    start_idx = (page - 1) * desks_per_page
    end_idx = min(start_idx + desks_per_page, len(desks))
    
    for i, desk in enumerate(desks):
        if start_idx <= i < end_idx:
            desk.style.display = "block"
        else:
            desk.style.display = "none"
    
    total_pages = (len(desks) + desks_per_page - 1) // desks_per_page
    if total_pages > 1:
        document.getElementById("page-info").textContent = f"(Page {page} of {total_pages})"
    else:
        document.getElementById("page-info").textContent = ""

def arrange_random(event=None):
    if not students:
        document.getElementById("status").innerHTML = "Please generate seating first"
        return
        
    shuffled = students.copy()
    random.shuffle(shuffled)
    assign_students_to_desks(shuffled)
    document.getElementById("status").innerHTML = "Arranged students randomly"

def arrange_alpha(event=None):
    if not students:
        document.getElementById("status").innerHTML = "Please generate seating first"
        return
        
    sorted_students = sorted(students)
    assign_students_to_desks(sorted_students)
    document.getElementById("status").innerHTML = "Arranged students alphabetically"

def assign_students_to_desks(student_list):
    # Clear all desks first
    for desk in desks:
        desk.classList.add("empty")
        desk.setAttribute("data-student", "")
        desk.innerHTML = ""
    
    # Assign students to desks
    for i, student in enumerate(student_list):
        if i < len(desks):
            desk = desks[i]
            desk.classList.remove("empty")
            desk.setAttribute("data-student", student)
            desk.innerHTML = student
            
            # Apply current view rotation
            desk.style.transform = "rotate(180deg)" if teacher_view else "rotate(0deg)"
            
            # Make student draggable
            desk.setAttribute("draggable", "true")
            desk.addEventListener("dragstart", create_proxy(drag))
    
    # Show current page
    show_page(current_page)

def allow_drop(event):
    event.preventDefault()

def drag(event):
    global dragged_student, dragged_desk
    dragged_student = event.target.getAttribute("data-student")
    dragged_desk = event.target
    event.target.classList.add("dragging")

def drop(event):
    event.preventDefault()
    global dragged_student, dragged_desk
    
    target_desk = event.target
    if not target_desk.classList.contains("desk"):
        target_desk = target_desk.closest(".desk")
    
    if dragged_student and target_desk and dragged_desk:
        target_student = target_desk.getAttribute("data-student")
        
        if target_student:
            dragged_desk.classList.remove("empty")
            dragged_desk.setAttribute("data-student", target_student)
            dragged_desk.innerHTML = target_student
        else:
            dragged_desk.classList.add("empty")
            dragged_desk.setAttribute("data-student", "")
            dragged_desk.innerHTML = ""
        
        target_desk.classList.remove("empty")
        target_desk.setAttribute("data-student", dragged_student)
        target_desk.innerHTML = dragged_student
        
        if teacher_view:
            target_desk.style.transform = "rotate(180deg)"
            dragged_desk.style.transform = "rotate(180deg)"
        else:
            target_desk.style.transform = "rotate(0deg)"
            dragged_desk.style.transform = "rotate(0deg)"
        
        if target_student:
            document.getElementById("status").innerHTML = f"Swapped {dragged_student} with {target_student}"
        else:
            document.getElementById("status").innerHTML = f"Moved {dragged_student} to empty desk"
    
    for desk in desks:
        desk.classList.remove("dragging")
    
    dragged_student = None
    dragged_desk = None

# Toggle between teacher and normal view
def toggle_view(event=None):
    global teacher_view
    teacher_view = not teacher_view
    
    for desk in desks:
        desk.style.transform = "rotate(180deg)" if teacher_view else "rotate(0deg)"
    
    if teacher_view:
        document.getElementById("status").innerHTML = "Teacher's View enabled"
    else:
        document.getElementById("status").innerHTML = "Normal View enabled"

# Set up event listeners
def setup_event_listeners():
    document.getElementById("generateBtn").addEventListener("click", create_proxy(generate_seating))
    document.getElementById("randomBtn").addEventListener("click", create_proxy(arrange_random))
    document.getElementById("alphaBtn").addEventListener("click", create_proxy(arrange_alpha))
    document.getElementById("toggleViewBtn").addEventListener("click", create_proxy(toggle_view))

setup_event_listeners()
document.getElementById("status").innerHTML = "Paste your student list and click 'Generate Seating'"
