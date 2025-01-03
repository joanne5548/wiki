from markdown2 import markdown
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
import os
from random import randint

from . import util

def index(request):
    if request.method == "POST":
        if 'q' in request.POST:
            return handle_search(request)
    
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry_view(request, entry_name):
    if request.method == "POST":
        if 'q' in request.POST:
            return handle_search(request)
    
    markdown_source = util.get_entry(entry_name)
    
    if markdown_source is not None:
        html = markdown(markdown_source)
        return render(request, "encyclopedia/entry_page.html", {
            "entry_name": entry_name,
            "html": html
        })
    
    return render(request, "encyclopedia/entry_page.html", {
        "error_message": "The requested entry does not exist."
    })

def handle_search_results(search_entries):
    search_results = {}
    for entry in search_entries:
        file_directory = os.path.join(settings.BASE_DIR, "entries", f"{entry}.md")
        with open(file_directory, 'r') as file:
            entry_markdown = ""
            file.readline() # skip the first line
            for line in file:
                entry_markdown += line
            
            entry_html = markdown(entry_markdown)
            entry_details = ''.join(BeautifulSoup(entry_html).findAll(text=True))
            
            entry_details_short = entry_details[:300]
            if (len(entry_details) > 300):
                entry_details_short = entry_details_short + "..."

        search_results[entry] = entry_details_short
    return search_results

def results_view(request, query):
    if request.method == "POST":
        if 'q' in request.POST:
            return handle_search(request)
    
    query_lower = query.lower()
    search_entries = [entry for entry in util.list_entries() if query_lower in entry.lower()]
    
    search_results = handle_search_results(search_entries)

    return render(request, "encyclopedia/results.html", {
        "search_query": query,
        "search_results": search_results,
    })

def create_view(request):
    if request.method == "POST":
        if 'q' in request.POST:
            return handle_search(request)
        elif 'title' in request.POST:
            title = request.POST['title']
            if not title:
                return render(request, "encyclopedia/create.html", {
                        "message": "Error: Please enter the title of the page."
                    })

            content = request.POST['content']
            print(content)
            
            search_results = entry_exists(title)
            if search_results:
                return render(request, "encyclopedia/create.html", {
                    "message": f"The entered item already exists in the wiki: ",
                    "entry_name": search_results[0]
                })
            
            write_markdown(title, content)
            return redirect('entry', title)
            
    return render(request, "encyclopedia/create.html")

def edit_view(request, entry_name):
    if request.method == "POST":
        if 'q' in request.POST:
            return handle_search(request)
        elif 'title' in request.POST:
            title = request.POST['title']
            if not title:
                return render(request, "encyclopedia/edit.html", {
                        "entry_name": entry_name,
                        "markdown_source": util.get_entry(entry_name),
                        "message": "Error: Please enter the title of the page."
                    })
            
            print(request.POST['content'])
            write_markdown(title, request.POST['content'], entry_name)
            return redirect('entry', title)

    return render(request, "encyclopedia/edit.html", {
        "entry_name": entry_name,
        "markdown_source": util.get_entry(entry_name)
    })

def random(request):
    entries_list = util.list_entries()
    path = request.META.get('HTTP_REFERER')
    if path:
        ind = path.find("wiki")
        path = path[ind + 5:]
        try:
            entry_index = entries_list.index(path)
        except ValueError:
            entry_index = -1

    rand_index = randint(0, len(entries_list) - 1)

    while entry_index == rand_index:
        rand_index = randint(0, len(entries_list) - 1)
    return redirect('entry', entries_list[rand_index])

def entry_exists(query):
    return [entry for entry in util.list_entries() if query.lower() == entry.lower()]

def handle_search(request):
    query = request.POST['q']
    search_result = entry_exists(query)
    
    if search_result:
        return redirect('entry', search_result[0])
    
    return redirect('results', query)

def write_markdown(title, content, old_name=None):
    file_directory = os.path.join(settings.BASE_DIR, "entries", f"{title}.md")

    if old_name: # When user edited the page
        old_directory = os.path.join(settings.BASE_DIR, "entries", f"{old_name}.md")
        os.rename(old_directory, file_directory)

    with open(file_directory, "w") as new_page:
        print(content)
        new_page.write(content)