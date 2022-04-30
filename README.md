# Study2Success

- [Study2Success](#study2success)
  - [Documentations](#documentations)
  - [Contributors](#contributors)
  - [Specifications](#specifications)
  - [Contributor Instructions](#contributor-instructions)
    - [Recommended editor](#recommended-editor)
    - [Writing documentation](#writing-documentation)
    - [Understanding directory structure](#understanding-directory-structure)
    - [Github flow](#github-flow)

## Access the App
Our app is currently launched at https://study2success.herokuapp.com !!!

## Documentations
For detailed documentations, please refer our hosted docs website [here](https://hoatnnguyen.github.io/Study2Success)


## Contributors
- [@Hoa Nguyen](https://github.com/HoaTNNguyen)
- [@Ngan Ngo](https://github.com/RachelNgo)
- [@Jerusalem Ilag](https://github.com/jeruilag)
- [@Abdullah Waheed](https://github.com/abdullahw1)


## Specifications
This is a project work in progress, for more information, please check out the [specifications document](./docs/Specification.md).


## Contributor Instructions
Recommended to read the below carefully before contributing to this project. Feel free to add cool things and features that you suggest people to know about.
### Recommended editor
  1. Vscode
      - Benefits: Understand multiple different format of code, including `md` documents.
      - Download link: [Click here](https://code.visualstudio.com/download)
      - Supported platforms: All(Windows/MacOS/Linux)

### Writing documentation
  1. Markdown `.md` documents
     - It's always recommended to keep clean documentation for the code you work on with a simple markdown document.
     - Check out Github markdown document for cool things you can do with markdown: https://guides.github.com/features/mastering-markdown/
     - Vscode also support downloading extensions that you can preview your markdown documents.

### Understanding directory structure
```
.
├── app                                         # Source code for applications
|   ├── myapp              
|   |   ├── static                              # CSS stylesheets, images, and javascript files needed for the app
|   |   ├── templates                           # contains all html files
|   |   |   ├── ...
|   |   ├── __init__.py                         # Set up flask and import library server
|   |   ├── forms.py                            # holds the code of all WTForms
|   |   ├── mdparser.py                         # holds the code helps extract markdown content into a list of Flashcards
|   |   ├── models.py                           # holds a list of Class that each representing the database table
|   |   ├── models_enum.py                      # Enum representing friend status in database
|   |   ├── models_methods.py                   # Functions returning all friends of a specified user
|   |   └── routes.py                           # hods all the routes of the app
|   └── run.py
├── docs                                        # Documentation folder (also used by [mkdocs](https://www.mkdocs.org) 
├── etc                                         # Contains all example files upload
├── mkdocs.yml                                  # Configuration file for mkdocs
└── requirements.txt                            # Dependency python packages
```

### Github flow
When making changes, please create a branch to work on it and file a PR to merge the changes. This really prevents
your changes to conflict with others a lot, you never know if somebody else is touching the same file as you. A really good documentation for the workflow that we should follow is [Github Workflow](https://guides.github.com/introduction/flow/).

### Generating documentation
Run the following command to view documentation in live:
```
mkdocs serve
```

To build an offline site that we can pass around:
```
mkdocs build
```

Then, simply copy all contents inside the generated `sites` folder and overwrite everything in the branch `docs`
The branch `docs` is reserved for launching the documentation site, Github Page will automatically build from that branch.


### Building herokuapp
Helpful documents that I followed for building the heroku app:
- [GeeksForGeeks-DeployHeroku](https://www.geeksforgeeks.org/deploy-python-flask-app-on-heroku/)
- [Heroku-PythonSupport](https://devcenter.heroku.com/articles/python-support)
